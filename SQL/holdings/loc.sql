CREATE DATABASE IF NOT EXISTS Franklin
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
USE Franklin;

-- --------------------------------------------------------------------
-- DATA MODEL NOTES\
--
-- == Specificity
--
--    Many tables adopt the schema of a mnemonic key value, a short
--    name, and a lengthy description.  The mnemonic key value is not
--    generally displayed; it is simply for ease of debugging while
--    reading the raw tables.  The short description should be displayed
--    in most UI contexts, followed by the lengthier description upon
--    user request.
-- --------------------------------------------------------------------


-- =====================================================================
--
--                 LOCATIONS, SUBLOCATIONS, SHELVING
--
-- =====================================================================

-- ---------------------------------------------------------------------
-- DATA MODEL NOTES
--
-- The location model reflects the MARC21 Holdings scheme.  The most
-- general location is assumed to be a physical building.  The
-- sublocation is assumed a room or designated area within the building.
-- The shelving location is assumed to be some sublocation-specific
-- designation.  Access policies apply here in the form of whether the
-- shelving is open to visitors and patrons and may vary by any of the
-- levels of location.
-- ---------------------------------------------------------------------


-- ---------------------------------------------------------------------
-- The list of available access policies for some particular location.
-- May be used by locations, sublocations, and individual shelving
-- locations.
--
CREATE TABLE IF NOT EXISTS `Location_Access_Policy` (
   ID            CHAR              PRIMARY KEY NOT NULL,
   name          VARCHAR(32),
   description   VARCHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `Location_Access_Policy` VALUES
   ( 'N', 'None',       'Staff access only' ),
   ( 'R', 'Restricted', 'Requires staff approval or supervision' ),
   ( 'O', 'Open',       'Publicly accessible' );


-- ---------------------------------------------------------------------
-- High-level location such as a building.
--
CREATE TABLE IF NOT EXISTS `Location` (
   ID            CHAR(8)           PRIMARY KEY NOT NULL,
   name          VARCHAR(32),
   description   VARCHAR(128),

   -- Mail or physical location.
   address1      VARCHAR(64),
   address2      VARCHAR(64),
   city          VARCHAR(32),
   state         VARCHAR(2),
   ZIP           VARCHAR(10),

   -- Geographic location.
   geo_lat       FLOAT,
   geo_long      FLOAT,

   -- Default access for this location.  Sublocation may override.
   Location_Access_Policy_ID CHAR NOT NULL DEFAULT 'O',

   FOREIGN KEY `access` ( `Location_Access_Policy_ID` )
      REFERENCES `Location_Access_Policy` ( `ID` )
      ON DELETE RESTRICT
      ON UPDATE CASCADE

) ENGINE = `InnoDB`;



-- ---------------------------------------------------------------------
-- Location within a building.
--
CREATE TABLE IF NOT EXISTS `Sublocation` (
   ID            CHAR(8)            PRIMARY KEY NOT NULL,
   Location_ID   CHAR(8)            NOT NULL,
   name          VARCHAR(32),
   description   VARCHAR(128),

   -- Default access for this sublocation.  Shelving may override.
   Location_Access_Policy_ID CHAR,

   FOREIGN KEY ( `Location_ID` ) REFERENCES `Location` ( `ID` )
      ON DELETE RESTRICT
      ON UPDATE CASCADE,

   FOREIGN KEY ( `Location_Access_Policy_ID` )
      REFERENCES `Location_Access_Policy` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE

) ENGINE = `InnoDB`;



-- ---------------------------------------------------------------------
-- The scheme for organizing items within a shelving location.
-- User-extensible.
--
CREATE TABLE IF NOT EXISTS `Shelving_Scheme` (
   ID             CHAR(8)       PRIMARY KEY NOT NULL,
   name           VARCHAR(32),
   description    VARCHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `Shelving_Scheme` VALUES
   ( 'CLASS',   'Classification',    'Subject classification (i.e., call number)' ),
   ( 'SERIAL',  'Serial number',     'Imposed serial number, location specific' ),
   ( 'AUTHOR',  'Author',            'Author name' ),
   ( 'TITLE',   'Title',             'Book title' ),
   ( 'DISPLAY', 'Display',           'Arranged for display' ),
   ( 'NONE',    'None',              'No shelving scheme' );



-- ---------------------------------------------------------------------
-- A shelving location within a continguous physical space (sublocation).
--
CREATE TABLE IF NOT EXISTS `Shelving_Location` (
   ID                         CHAR(8)         PRIMARY KEY NOT NULL,
   Sublocation_ID             CHAR(8),
   name                       VARCHAR(32),
   description                VARCHAR(128),

   Shelving_Scheme_ID         CHAR(8),
   Location_Access_Policy_ID  CHAR,

   FOREIGN KEY ( `Sublocation_ID` ) REFERENCES `Sublocation` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE,

   FOREIGN KEY ( `Shelving_Scheme_ID` ) REFERENCES `Shelving_Scheme` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE,

   FOREIGN KEY ( `Location_Access_Policy_ID` )
     REFERENCES `Location_Access_Policy` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;



-- ---------------------------------------------------------------------
-- The location of an electronic resource, typically accessible via
-- HTTP.
--
CREATE TABLE IF NOT EXISTS `Electronic_Location` (
   ID            INTEGER(6)    PRIMARY KEY AUTO_INCREMENT,

   -- URI elements
   host          VARCHAR(128),
   port          INTEGER(5),
   scheme        VARCHAR(8)    DEFAULT 'http',
   path          VARCHAR(256),
   login         VARCHAR(16),
   password      VARCHAR(128),
   args          VARCHAR(256)  DEFAULT '',

   os_type       ENUM (
                      'MacOS',
                      'Linux',
                      'Windows',
                      'Other'
                   )           DEFAULT 'Other',

   compression   VARCHAR(64)   DEFAULT 'none',
   file_size     INTEGER(16),
   mime_format   VARCHAR(64)   DEFAULT 'text/plain'

) ENGINE = `InnoDB`;
