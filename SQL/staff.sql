CREATE DATABASE IF NOT EXISTS Franklin
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
USE Franklin;

-- =====================================================================
--
--                 STAFF, DEPARTMENTS, and ROLES
--
-- =====================================================================

-- ---------------------------------------------------------------------
-- Describes a particular kind of role a member of staff can have.
-- User-extensible, but programmatically implelmented.
--
CREATE TABLE IF NOT EXISTS `Staff_Role` (
   ID           CHAR(8)            PRIMARY KEY NOT NULL,
   name         VARCHAR(32),
   description  VARCHAR(132)
) ENGINE = `InnoDB`;

INSERT INTO `Staff_Role` VALUES
   ( 'STAFF',   'Staff',       'All staff' ),
   ( 'STACK',   'Stacks',      'Stacks maintenance and shelving' ),
   ( 'CATALOG', 'Cataloging',  'Cataloging and technical service' );



-- ---------------------------------------------------------------------
-- A group or department among the staff.
--
CREATE TABLE IF NOT EXISTS `Staff_Department` (
   ID           CHAR(8)            PRIMARY KEY NOT NULL,
   name         VARCHAR(32),
   description  VARCHAR(128),
   Location_ID  CHAR(8),          -- optional location ID

   FOREIGN KEY ( `Location_ID` ) REFERENCES `Location` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE

) ENGINE = `InnoDB`;

INSERT INTO `Staff_Department` VALUES
   ( 'GEN',     'General',      'All departments', NULL );



-- ---------------------------------------------------------------------
-- Individual staff members.
--
CREATE TABLE IF NOT EXISTS `Staff` (

   login        VARCHAR(32) PRIMARY KEY NOT NULL,

   last_name    VARCHAR(64) NOT NULL,
   first_name   VARCHAR(64),
   title        VARCHAR(64),

   dept         CHAR(8),

   FOREIGN KEY ( `dept` ) REFERENCES `Staff_Department` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;

INSERT INTO `Staff` VALUES
   ( 'SYSTEM', 'Franklin', 'System', 'Franklin System', 'GEN'  );



-- ---------------------------------------------------------------------
-- Join table for staff members and their roles.
--
CREATE TABLE IF NOT EXISTS `Staff_Role_Map` (
   login           VARCHAR(32)   NOT NULL,
   Staff_Role_ID   CHAR(8)       NOT NULL,

   UNIQUE INDEX `staff_role` ( `login`, `Staff_Role_ID` ),

   FOREIGN KEY ( `login` ) REFERENCES `Staff` ( `login` )
      ON DELETE CASCADE
      ON UPDATE CASCADE,

   FOREIGN KEY ( `Staff_Role_ID` )
      REFERENCES `Staff_Role` ( `ID` )
      ON DELETE CASCADE
      ON UPDATE CASCADE

) ENGINE = `InnoDB`;
