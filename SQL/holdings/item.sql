CREATE DATABASE IF NOT EXISTS franklin
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
USE franklin;


-- =====================================================================
--
--                 ITEMS, ITEM NOTES, and ITEM ACTIONS
--
-- =====================================================================

-- ---------------------------------------------------------------------
-- DATA MODEL NOTES
--
-- The location model is strictly hierarchical in three levels.  The
-- Item need only specify shelving location; there is a unique path to
-- the root of the location tree from that node.
-- ---------------------------------------------------------------------


-- ---------------------------------------------------------------------
-- Individually held unit.  This is most likely going to be a single
-- copy of a book.
--
CREATE TABLE IF NOT EXISTS `item` (

   -- ID is most typically the barcode label of the individual item.  It
   -- can conceivably be a randomly-generated unique key.  This way we
   -- can have anonymous serial unit references with holdings and
   -- location information.
   --
   ID                      VARCHAR(32)  PRIMARY KEY NOT NULL,

   -- Reference to bibliographic unit.
   ctl_num                 CHAR(32),

   copy                    INTEGER(2)        DEFAULT 1,

   -- Usually an item will have either a physical location or an
   -- electronic location.  It does arise that a physical printout has a
   -- master electronic location.  Thus conceivably we can have both.
   --
   shelving_location_ID    CHAR(8),
   electronic_location_ID  INTEGER(8),

   -- Content and form descriptors.  Carrier_Type_ID and one of the
   -- other two descriptors uniquely determine the appropriate carrier
   -- type.
   --
   content_type_ID         CHAR(8)           DEFAULT 'TEXT',
   media_type_ID           CHAR(8)           DEFAULT 'DIRECT',
   carrier_type_ID         CHAR(8)           DEFAULT 'CODEX',


   INDEX `bib_item` ( `ID`, `ctl_num` ),

   FOREIGN KEY ( `ctl_num` ) REFERENCES `MARC_leader` ( `ctl_num` )
      ON DELETE CASCADE
      ON UPDATE CASCADE,

   FOREIGN KEY ( `shelving_location_ID` )
      REFERENCES `shelving_location` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE,

   FOREIGN KEY ( `electronic_location_ID` )
      REFERENCES `electronic_location` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE,

   -- Content_Type and Media_Type are foreign keys, but Carrier_Type is
   -- not because we reuse the IDs
   --
   FOREIGN KEY ( `content_type_ID` )
      REFERENCES `content_type` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE,

   FOREIGN KEY ( `media_type_ID` )
      REFERENCES `media_type` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE


) ENGINE = `InnoDB`;







-- ---------------------------------------------------------------------
-- Predetermined types of notes to attach to items.  User-extensible.
--
CREATE TABLE IF NOT EXISTS `item_note_type` (
   ID           CHAR(8)      PRIMARY KEY NOT NULL,
   name         CHAR(32),
   description  CHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `item_note_type` VALUES
   ( 'UNSPEC', 'General',          'General note' ),
   ( 'CUST',   'Custodial',        'History of custody for this item' ),
   ( 'FORM',   'Format notes',     'Annotations for media types, formats, etc. not directly covered' ),
   ( 'MARKS',  'Identifying mark', 'Marks or other distinctive identifying features' ),
   ( 'ORIG',   'Original form',    'How the material for an item first came about' ),
   ( 'BIND',   'Binding note',     'Comments about the material container' ),
   ( 'ACTION', 'Action required',  'An action must be taken on this item' );



-- ---------------------------------------------------------------------
-- For notes of type ACTION, a list of predetermined actions to take.
-- User-extensible.
--
CREATE TABLE IF NOT EXISTS `item_action_type` (
  ID           CHAR(8)      PRIMARY KEY NOT NULL,
  name         CHAR(32),
  description  CHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `item_action_type` VALUES
   ( 'UNSPEC',   'Special',   '' ),
   ( 'ACCEDE',   'Accede',    'Obtain this item initially.' ),
   ( 'INSPECT',  'Inspect',   'Inspect this item.' ),
   ( 'REVIEW',   'Review',    'Examine item for policy change.' ),
   ( 'REPAIR',   'Repair',    'Repair or restore this item' ),
   ( 'WITHDR',   'Withdraw',  'Withdraw this item from the collection' ),
   ( 'DESTROY',  'Destroy',   'Destroy this item.' ),
   ( 'TRANSFER', 'Transfer',  'Transfer item to new location.' ),
   ( 'APPRAISE', 'Appraise',  'Determine monetary value.' ),
   ( 'DIGIT',    'Digitize',  'Convert this item to digital form.' ),
   ( 'REPR',     'Reproduce', 'Make a physical copy of this item.' );



-- ---------------------------------------------------------------------
-- Notes to attach to an item.
--
CREATE TABLE IF NOT EXISTS `item_note` (
   ID                 BIGINT(32)    PRIMARY KEY NOT NULL AUTO_INCREMENT,
   item_ID            VARCHAR(32),
   item_note_type_ID  CHAR(8)       DEFAULT 'UNSPEC',
   ts                 TIMESTAMP     DEFAULT NOW(),
   agent              VARCHAR(32)   DEFAULT 'SYSTEM',
   detail             VARCHAR(256),

   FOREIGN KEY ( `item_ID` ) REFERENCES `item` ( `ID` )
     ON DELETE CASCADE
     ON UPDATE CASCADE,

   FOREIGN KEY ( `item_note_type_ID` )
     REFERENCES `item_note_type` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE,

   FOREIGN KEY ( `agent` ) REFERENCES `staff` ( `login` )
     ON DELETE SET NULL
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;



-- ---------------------------------------------------------------------
-- Maintain at most one action item note for each item and action type,
-- and provide a place to attach action detail records.
--
CREATE TABLE IF NOT EXISTS `item_action_note` (
  ID                   BIGINT(32)  PRIMARY KEY NOT NULL AUTO_INCREMENT,
  item_note_ID         BIGINT(32)  NOT NULL,
  item_action_type_ID  CHAR(8)     NOT NULL,

  UNIQUE INDEX `action_type` ( `item_note_ID`, `item_action_type_ID` ),

  FOREIGN KEY ( `Item_Note_ID` ) REFERENCES `Item_Note` ( `ID` )
     ON DELETE CASCADE
     ON UPDATE CASCADE,

  FOREIGN KEY ( `item_action_type_ID` )
     REFERENCES `item_action_type` ( `ID` )
     ON DELETE CASCADE
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;



-- ---------------------------------------------------------------------
-- Establishes authority for carrying out or having carried out an item
-- action.
--
CREATE TABLE IF NOT EXISTS `item_action_note_detail` (
  item_action_note_ID  BIGINT(32)   NOT NULL,

  -- Date/time at which the outcome for this action was set.
  ts_action            TIMESTAMP                 DEFAULT NOW(),

  agent                VARCHAR(32)               DEFAULT 'SYSTEM',

  note                 VARCHAR(256),

  authority            ENUM (
                            'Policy',      -- automatic, by virtue of policy
                            'Direction',   -- responsible staff specifically directed
                            'Staff'        -- staff's own recognizance
                            )
                                                 DEFAULT 'Staff',
  method               ENUM (
                            'Automated',   -- unattended automatic operation
                            'Online',      -- external computer access
                            'Manual',      -- physical handling of material
                            'Visual',      -- visual examination
                            'Delegated',   -- external third-party operation
                            'Other'
                            )                    DEFAULT 'Other',
  outcome              ENUM (
                            'Pending',     -- waiting to be accomplished
                            'Deferred',    -- put on hold, reason in notes
                            'Blocked',     -- cannot proceed for external reasons
                            'Canceled',    -- action canceled
                            'Completed'    -- completed successfully
                            )
                                                 DEFAULT 'Pending',

  FOREIGN KEY ( `item_action_note_ID` )
     REFERENCES `item_action_note` ( `ID` )
     ON DELETE CASCADE
     ON UPDATE CASCADE,

  FOREIGN KEY ( `agent` ) REFERENCES `staff` ( `login` )
     ON DELETE SET NULL
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;
