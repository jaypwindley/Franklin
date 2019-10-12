CREATE DATABASE IF NOT EXISTS franklin
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
USE franklin;

-- =====================================================================
--
--                 MULTIPART SERIALS HOLDINGS
--
-- =====================================================================




-- ---------------------------------------------------------------------
-- Annotation for serial bibliographic units, describing the holdings
-- policy, retention, and enumeration.
--
CREATE TABLE IF NOT EXISTS `multipart_profile` (
   ctl_num      CHAR(32) NOT NULL PRIMARY KEY,

   -- Acquisition and retention policies.
   retention    ENUM (
                     'all',         -- all issues retained
                     'interval',    -- only the last few retained
                     'current'      -- only current issue
                     )
                                  DEFAULT 'current',
   reception    ENUM (
                     'ongoing',     -- subscription continues
                     'ended',       -- subscription ended
                     'ad hoc'       -- issues purchased individually
                     )
                                  DEFAULT 'ad hoc',

   -- Publication intervals.
   --    frequency: issue rate in each per_interval
   --       can be 0.5 to indicate biennoal, bimonthly, biweekly
   --    per_interval: time denominator, one of: year, month, week, day, null
   --       null indicates uncodable interval,
   --
   --     Logical Rate                  frequency    per_interval
   --     -------------------------------------------------------
   --       Annual                           1         Y
   --       Bimonthly                        0.5       M
   --       Continuously updated (web page)  1         null
   --       Semiweekly                       2         W
   --       Monthly                          1         M
   --       Daily                            1         D
   --       Quarterly                        4         Y
   --       Biweekly                         0.5       W
   --       Semimonthly                      2         M
   --       Semiannual                       2         Y
   --       Biennial                         0.5       Y
   --       Weekly                           1         W
   --       Completely irregular             0         null
   frequency    FLOAT,
   per_interval ENUM ( 'Y', 'M', 'W', 'D' ),

   -- What supplementary material this publication provides.
   unnumerated  SET ( 'supplement', 'index', 'other' ),

   -- How this serial captions its enumeration levels.  MARC21 supports
   -- 4 enumeration levels.  Set to NULL if serial is not enumerated.
   --
   enum_cap_1   VARCHAR(12) DEFAULT 'volume',
   enum_cap_2   VARCHAR(12) DEFAULT 'part',
   enum_cap_3   VARCHAR(12) DEFAULT 'issue',
   enum_cap_4   VARCHAR(12) DEFAULT 'section',

   -- At each enumeration level, how many parts per higher enumeration.
   -- enum_div_2 would be how many 'parts' per 'volume', in the defaults
   -- from above.  Set to zero for divisions that aren't applicable.
   --
   enum_div_2   INTEGER(2),
   enum_div_3   INTEGER(2),
   enum_div_4   INTEGER(2),

   -- How this serial captions its chronology levels.  MARC21 supports 3
   -- chronology levels.  Set to NULL if serial is not chronologically
   -- captioned.
   --
   chron_cap_1  VARCHAR(12) DEFAULT 'year',
   chron_cap_2  VARCHAR(12) DEFAULT 'month', -- cf. also 'season'
   chron_cap_3  VARCHAR(12) DEFAULT 'day',   -- cf. also 'week', 'day'

   FOREIGN KEY ( `ctl_num` ) REFERENCES `MARC_leader` ( `ctl_num` )
      ON DELETE CASCADE
      ON UPDATE CASCADE

) ENGINE = `InnoDB`;
