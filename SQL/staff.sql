CREATE DATABASE IF NOT EXISTS franklin
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
USE franklin;

-- =====================================================================
--
--                 STAFF, DEPARTMENTS, and ROLES
--
-- =====================================================================

-- ---------------------------------------------------------------------
-- Describes a particular kind of role a member of staff can have.
-- User-extensible, but programmatically implelmented.
--
CREATE TABLE IF NOT EXISTS `staff_role` (
   ID           CHAR(8)            PRIMARY KEY NOT NULL,
   name         VARCHAR(32),
   description  VARCHAR(132)
) ENGINE = `InnoDB`;

INSERT INTO `staff_role` VALUES
   ( 'STAFF',   'Staff',       'All staff' ),
   ( 'STACK',   'Stacks',      'Stacks maintenance and shelving' ),
   ( 'CATALOG', 'Cataloging',  'Cataloging and technical service' );



-- ---------------------------------------------------------------------
-- A group or department among the staff.
--
CREATE TABLE IF NOT EXISTS `staff_department` (
   ID           CHAR(8)            PRIMARY KEY NOT NULL,
   name         VARCHAR(32),
   description  VARCHAR(128),
   location_ID  CHAR(8),          -- optional location ID

   FOREIGN KEY ( `location_ID` ) REFERENCES `location` ( `ID` )
      ON DELETE SET NULL
      ON UPDATE CASCADE

) ENGINE = `InnoDB`;

INSERT INTO `staff_department` VALUES
   ( 'GEN',     'General',      'All departments', NULL );



-- ---------------------------------------------------------------------
-- Individual staff members.
--
CREATE TABLE IF NOT EXISTS `staff` (

   login        VARCHAR(32) PRIMARY KEY NOT NULL,

   last_name    VARCHAR(64) NOT NULL,
   first_name   VARCHAR(64),
   title        VARCHAR(64),

   dept         CHAR(8),

   FOREIGN KEY ( `dept` ) REFERENCES `staff_department` ( `ID` )
     ON DELETE SET NULL
     ON UPDATE CASCADE

) ENGINE = `InnoDB`;

INSERT INTO `staff` VALUES
   ( 'SYSTEM', 'Franklin', 'System', 'Franklin System', 'GEN'  );



-- ---------------------------------------------------------------------
-- Join table for staff members and their roles.
--
CREATE TABLE IF NOT EXISTS `staff_role_map` (
   login           VARCHAR(32)   NOT NULL,
   staff_role_ID   CHAR(8)       NOT NULL,

   UNIQUE INDEX `staff_role` ( `login`, `staff_role_ID` ),

   FOREIGN KEY ( `login` ) REFERENCES `staff` ( `login` )
      ON DELETE CASCADE
      ON UPDATE CASCADE,

   FOREIGN KEY ( `staff_role_ID` )
      REFERENCES `staff_role` ( `ID` )
      ON DELETE CASCADE
      ON UPDATE CASCADE

) ENGINE = `InnoDB`;
