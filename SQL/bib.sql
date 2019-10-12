CREATE DATABASE IF NOT EXISTS franklin
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
USE franklin;

-- -------------------------------------------------------------------------------------------------
-- DATA MODEL NOTES
--
-- The control number ctl_num is generally composed of the cataloguing source (i.e., as a namespace)
-- and the 001 control field value as the unique identifier within the namespace.  E.g., DLC177342
-- for a Library of Congress catalog numer.
--
-- MARC_Leader is the parent table.  All other tables use the ctl_num field as a foreign key into
-- the table such that deleting the MARC_Leader record for a bibliographic entry deletes all
-- subordinate data.  Ditto for updates.
--
-- Control fields have no subfields or indicators, hence their values are stored directly.  Their
-- tag values cannot duplicate within a record, so no subsequencing is required.
--
-- For Indicators and Fields, a triple of (ctl_num, tag, seq) identifies a specific tag.  This is
-- because certain tags such as 6xx subject fields may repeat.  Hence seq is a unique identifier
-- within the namespace (ctl_num, tag) to identify a specific instance of a tag.
--
-- Indicators are stored separately such that if a tag has no indicators then no row need be stored.
-- If one or both indicators are specified, then a row is stored.
-- -------------------------------------------------------------------------------------------------


-- -------------------------------------------------------------------------------------------------
-- MARC 21 leader information from the interchange.  There is a 1:1 correspondence between
-- MARC_Leader rows and bibliographic entities.
--
CREATE TABLE IF NOT EXISTS MARC_leader (
       ctl_num	    CHAR(32)          NOT NULL UNIQUE KEY,
       val	    CHAR(25)
) ENGINE = 'InnoDB';


-- -------------------------------------------------------------------------------------------------
-- MARC 21 control fields, tags 001 to 009.  These fields do not have subfield codes or indicators.
--
CREATE TABLE IF NOT EXISTS MARC_control_fields (
       ctl_num	    CHAR(32)	      NOT NULL,
       tag	    CHAR(3)           NOT NULL,
       val	    VARCHAR(128),

       PRIMARY KEY ( ctl_num, tag ),
       INDEX (`ctl_num` ),
       CONSTRAINT FOREIGN KEY ( `ctl_num` ) REFERENCES `MARC_leader` ( `ctl_num` )
       		  ON DELETE CASCADE
		  ON UPDATE CASCADE

) ENGINE = 'InnoDB';


-- -------------------------------------------------------------------------------------------------
-- MARC 21 indicators for each tag.  For duplicated tags, use seq to disambiguate.  If a tag has all
-- default indicators, there will be no row in this table for them.
--
CREATE TABLE IF NOT EXISTS MARC_indicators (
       ctl_num	     CHAR(32)         NOT NULL,
       tag	     CHAR(3)          NOT NULL,
       seq	     TINYINT          NOT NULL DEFAULT  1,
       ind_1	     CHAR                 NULL DEFAULT ' ',
       ind_2	     CHAR                 NULL DEFAULT ' ',

       PRIMARY KEY ( ctl_num, tag, seq ),
       INDEX (`ctl_num` ),
       CONSTRAINT FOREIGN KEY ( `ctl_num` ) REFERENCES `MARC_leader` ( `ctl_num` )
       		  ON DELETE CASCADE
		  ON UPDATE CASCADE

) ENGINE = 'InnoDB';


-- -------------------------------------------------------------------------------------------------
-- MARC 21 field data for each tag and field.  For duplicated tags, use seq to disambiguate.  Tags
-- may appear out of order in input but are "corrected" to numerical order on storage and output.
-- Codes may appear in any order, even non-alphabetical, and may be repeated (e.g., 'z' for refined
-- geography qualifiers on 650 subject headings.  Subfield codes must preserve order, hence 'pos'
-- gives original order in input.
--
CREATE TABLE IF NOT EXISTS MARC_fields (
       ctl_num	    CHAR(32)          NOT NULL,
       tag	    CHAR(3)           NOT NULL,
       seq	    TINYINT           NOT NULL DEFAULT  1,
       pos          TINYINT           NOT NULL DEFAULT  1,
       code	    CHAR              NOT NULL DEFAULT 'a',
       val	    VARCHAR(2048),

       INDEX ( ctl_num, tag, seq, pos ),
       INDEX (`ctl_num` ),
       CONSTRAINT FOREIGN KEY ( `ctl_num` ) REFERENCES `MARC_leader` ( `ctl_num` )
       		  ON DELETE CASCADE
		  ON UPDATE CASCADE

) ENGINE = 'InnoDB';


-- -------------------------------------------------------------------------------------------------
-- Keywords to aid in searches.  Ctl_num obviously gives the record in which the keyword is found.
-- Namespace describes whether it's a title, author, or subject keyword so that searches can be
-- restricted to a particular domain.  For records that have more than one instance of a kind of
-- namespace (e.g., a record with several subject listings), instance distinguishes among them in
-- the same record.  Offset describes the position of the keyword in its instance.  This is so a
-- search algorithm can determine whether two words are adjacent.
--
CREATE TABLE IF NOT EXISTS bib_keywords (
       ctl_num	    CHAR(32)		NOT NULL,
       namespace    ENUM (
       		       '-', -- none
		       'A', -- author
		       'S', -- subject
		       'T'  -- title
		       )                           DEFAULT '-',
       keyword      VARCHAR(256)        NOT NULL,
       instance     SMALLINT(2)                    DEFAULT 0,
       offset       SMALLINT(2)                    DEFAULT 0,

       UNIQUE ( `ctl_num`, `namespace`, `keyword`, `instance`, `offset` ),
       INDEX( `keyword` ),
       INDEX( `keyword`, `namespace` ),
       CONSTRAINT FOREIGN KEY ( `ctl_num` ) REFERENCES `MARC_leader` ( `ctl_num` )
       	       ON DELETE CASCADE
	       ON UPDATE CASCADE
) ENGINE = 'InnoDB';
