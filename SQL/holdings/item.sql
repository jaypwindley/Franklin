CREATE DATABASE IF NOT EXISTS Franklin
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
USE Franklin;


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
CREATE TABLE IF NOT EXISTS `Item` (

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
   Shelving_Location_ID    CHAR(8),
   Electronic_Location_ID  INTEGER(8),

   -- Content and form descriptors.  Carrier_Type_ID and one of the
   -- other two descriptors uniquely determine the appropriate carrier
   -- type.
   --
   Content_Type_ID         CHAR(8)           DEFAULT 'TEXT',
   Media_Type_ID           CHAR(8)           DEFAULT 'DIRECT',
   Carrier_Type_ID         CHAR(8)           DEFAULT 'CODEX',


   INDEX `bib_item` ( `ID`, `ctl_num` ),

   FOREIGN KEY ( `ctl_num` ) REFERENCES `MARC_Leader` ( `ctl_num` )
      ON DELETE CASCADE
      ON UPDATE CASCADE,

   FOREIGN KEY ( `Shelving_Location_ID` )
      REFERENCES `Shelving_Location` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE,

   FOREIGN KEY ( `Electronic_Location_ID` )
      REFERENCES `Electronic_Location` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE,

   -- Content_Type and Media_Type are foreign keys, but Carrier_Type is
   -- not because we reuse the IDs
   --
   FOREIGN KEY ( `Content_Type_ID` )
      REFERENCES `Content_Type` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE,

   FOREIGN KEY ( `Media_Type_ID` )
      REFERENCES `Media_Type` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE


) ENGINE = `InnoDB`;







-- ---------------------------------------------------------------------
-- Predetermined types of notes to attach to items.  User-extensible.
--
CREATE TABLE IF NOT EXISTS `Item_Note_Type` (
   ID           CHAR(8)      PRIMARY KEY NOT NULL,
   name         CHAR(32),
   description  CHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `Item_Note_Type` VALUES
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
CREATE TABLE IF NOT EXISTS `Item_Action_Type` (
  ID           CHAR(8)      PRIMARY KEY NOT NULL,
  name         CHAR(32),
  description  CHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `Item_Action_Type` VALUES
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
CREATE TABLE IF NOT EXISTS `Item_Note` (
   ID                 BIGINT(32)    PRIMARY KEY NOT NULL AUTO_INCREMENT,
   Item_ID            VARCHAR(32),
   Item_Note_Type_ID  CHAR(8)       DEFAULT 'UNSPEC',
   ts                 TIMESTAMP     DEFAULT NOW(),
   agent              VARCHAR(32)   DEFAULT 'SYSTEM',
   detail             VARCHAR(256),

   FOREIGN KEY ( `Item_ID` ) REFERENCES `Item` ( `ID` )
     ON DELETE CASCADE
     ON UPDATE CASCADE,

   FOREIGN KEY ( `Item_Note_Type_ID` )
     REFERENCES `Item_Note_Type` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE,

   FOREIGN KEY ( `agent` ) REFERENCES `Staff` ( `login` )
     ON DELETE SET NULL
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;



-- ---------------------------------------------------------------------
-- Maintain at most one action item note for each item and action type,
-- and provide a place to attach action detail records.
--
CREATE TABLE IF NOT EXISTS `Item_Action_Note` (
  ID                   BIGINT(32)  PRIMARY KEY NOT NULL AUTO_INCREMENT,
  Item_Note_ID         BIGINT(32)  NOT NULL,
  Item_Action_Type_ID  CHAR(8)     NOT NULL,

  UNIQUE INDEX `action_type` ( `Item_Note_ID`, `Item_Action_Type_ID` ),

  FOREIGN KEY ( `Item_Note_ID` ) REFERENCES `Item_Note` ( `ID` )
     ON DELETE CASCADE
     ON UPDATE CASCADE,

  FOREIGN KEY ( `Item_Action_Type_ID` )
     REFERENCES `Item_Action_Type` ( `ID` )
     ON DELETE CASCADE
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;



-- ---------------------------------------------------------------------
-- Establishes authority for carrying out or having carried out an item
-- action.
--
CREATE TABLE IF NOT EXISTS `Item_Action_Note_Detail` (
  Item_Action_Note_ID  BIGINT(32)   NOT NULL,

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

  FOREIGN KEY ( `Item_Action_Note_ID` )
     REFERENCES `Item_Action_Note` ( `ID` )
     ON DELETE CASCADE
     ON UPDATE CASCADE,

  FOREIGN KEY ( `agent` ) REFERENCES `Staff` ( `login` )
     ON DELETE SET NULL
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;
