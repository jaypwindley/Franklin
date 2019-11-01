CREATE DATABASE IF NOT EXISTS franklin
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
USE franklin;

-- -------------------------------------------------------------------------------------------------
-- DATA MODEL NOTES\
--
-- == Specificity
--
--    Many tables adopt the schema of a mnemonic key value, a short name, and a lengthy description.
--    The mnemonic key value is not generally displayed; it is simply for ease of debugging while
--    reading the raw tables.  The short description should be displayed in most UI contexts,
--    followed by the lengthier description upon user request.
--    ----------------------------------------------------------------------------------------------


--
-- LOCATIONS, SUBLOCATIONS, SHELVING
--

-- -------------------------------------------------------------------------------------------------
-- DATA MODEL NOTES
--
-- The location model reflects the MARC21 Holdings scheme.  The most general location is assumed to
-- be a physical building.  The sublocation is assumed a room or designated area within the
-- building.  The shelving location is assumed to be some sublocation-specific designation.  Access
-- policies apply here in the form of whether the shelving is open to visitors and patrons and may
-- vary by any of the levels of location.
-- -------------------------------------------------------------------------------------------------


-- -------------------------------------------------------------------------------------------------
-- The list of available access policies for some particular location.  May be used by locations,
-- sublocations, and individual shelving locations.
--
CREATE TABLE IF NOT EXISTS `access_policy` (
   ID            CHAR              PRIMARY KEY NOT NULL,
   name          VARCHAR(32),
   description   VARCHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `access_policy` VALUES
   ( 'N', 'None',       'Staff access only' ),
   ( 'R', 'Restricted', 'Requires staff approval or supervision' ),
   ( 'O', 'Open',       'Publicly accessible' );


-- -------------------------------------------------------------------------------------------------
-- High-level location such as a building.
--
CREATE TABLE IF NOT EXISTS `location` (
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
   access_policy_ID CHAR NOT NULL DEFAULT 'O',

   FOREIGN KEY `access` ( `access_policy_ID` )
      REFERENCES `access_policy` ( `ID` )
      ON DELETE RESTRICT
      ON UPDATE CASCADE

) ENGINE = `InnoDB`;


-- -------------------------------------------------------------------------------------------------
-- Location within a building.
--
CREATE TABLE IF NOT EXISTS `sublocation` (
   ID            CHAR(8)            PRIMARY KEY NOT NULL,
   location_ID   CHAR(8)            NOT NULL,
   name          VARCHAR(32),
   description   VARCHAR(128),

   -- Default access for this sublocation.  Shelving may override.
   access_policy_ID CHAR,

   FOREIGN KEY ( `location_ID` ) REFERENCES `location` ( `ID` )
      ON DELETE RESTRICT
      ON UPDATE CASCADE,

   FOREIGN KEY ( `access_policy_ID` )
      REFERENCES `access_policy` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE

) ENGINE = `InnoDB`;


-- -------------------------------------------------------------------------------------------------
-- The scheme for organizing items within a shelving location.  User-extensible.
--
CREATE TABLE IF NOT EXISTS `shelving_scheme` (
   ID             CHAR(8)       PRIMARY KEY NOT NULL,
   name           VARCHAR(32),
   description    VARCHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `shelving_scheme` VALUES
   ( 'CLASS',   'Classification',    'Subject classification (i.e., call number)' ),
   ( 'SERIAL',  'Serial number',     'Imposed serial number, location specific' ),
   ( 'AUTHOR',  'Author',            'Author name' ),
   ( 'TITLE',   'Title',             'Book title' ),
   ( 'DISPLAY', 'Display',           'Arranged for display' ),
   ( 'NONE',    'None',              'No shelving scheme' );


-- -------------------------------------------------------------------------------------------------
-- A shelving location within a continguous physical space (sublocation).
--
CREATE TABLE IF NOT EXISTS `shelving_location` (
   ID                         CHAR(8)         PRIMARY KEY NOT NULL,
   sublocation_ID             CHAR(8),
   name                       VARCHAR(32),
   description                VARCHAR(128),

   shelving_scheme_ID         CHAR(8),
   access_policy_ID  CHAR,

   FOREIGN KEY ( `sublocation_ID` ) REFERENCES `sublocation` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE,

   FOREIGN KEY ( `shelving_scheme_ID` ) REFERENCES `shelving_scheme` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE,

   FOREIGN KEY ( `access_policy_ID` )
     REFERENCES `access_policy` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;


-- -------------------------------------------------------------------------------------------------
-- The location of an electronic resource, typically accessible via HTTP.
--
CREATE TABLE IF NOT EXISTS `electronic_location` (
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
