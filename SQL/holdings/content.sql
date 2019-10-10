CREATE DATABASE IF NOT EXISTS Franklin
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci;
USE Franklin;

-- =====================================================================
--
--                 CONTENT TYPES AND MEDIA
--
-- =====================================================================


-- ---------------------------------------------------------------------
-- Describes the kind of information represented in the item, as opposed
-- to the physical method by which the information is conveyed or
-- presented.  This is the inherent type of information.  It is
-- user-extensible, but the preformatted ones here are those from the
-- MARC21 classifications.
--
CREATE TABLE IF NOT EXISTS `Content_Type` (
   ID          CHAR(8)        PRIMARY KEY NOT NULL,
   name        VARCHAR(32),
   description VARCHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `Content_Type` VALUES
   ( 'CART',    'cartographic',        'map, globe, or similar geographic information' ),
   ( 'ELEC',    'electronic',          'machine-interpretable instruction (e.g., software)' ),
   ( 'PERF',    'notated performance', 'dance, music, etc. in written form' ),
   ( 'SOUND',   'sounds',              'audible content (language independent)' ),
   ( 'SPOKEN',  'spoken language',     'audible content (language specific)' ),
   ( 'STILL',   'still image',         'photos, paintings, etc.' ),
   ( 'TACTILE', 'tactile',             'intended to be touched, Braille, etc.' ),
   ( 'FORM',    'physical form',       'physical forms such as sculpture' ),
   ( 'TEXT',    'readable text',       'readable text, any language' ),
   ( 'VISUAL',  'visible object',      'object meant to be seen, e.g., preserved specimen' ),
   ( 'MOVING',  'moving image',        'motion picture, whether optical or digital' ),
   ( 'OTHER',   'other',               'Unknown or undefined content' );



-- ---------------------------------------------------------------------
-- Suggests whether some kind of mediation is necessary to present to
-- the content to a patron.  The default is DIRECT which is simply
-- looking at the medium to recieve the information.
--
CREATE TABLE IF NOT EXISTS `Media_Type` (
   ID             CHAR(8)          PRIMARY KEY NOT NULL,
   name           VARCHAR(32),
   description    VARCHAR(128)
) ENGINE = `InnoDB`;

INSERT INTO `Media_Type` VALUES
   ( 'AUDIO',     'sound recording', 'music CD, phonograph record, computer sound file' ),
   ( 'ELEC',      'computer',        'software or programmatic content' ),
   ( 'MICFORM',   'microform',       'microfilm, microfiche, etc.' ),
   ( 'MICSCOPE',  'microscopic',     'microscopic specimen' ),
   ( 'PROJ',      'projected',       'transparent still forms requiring light transmission' ),
   ( 'STEREO',    'stereoscopic',    'anaglyphs etc. requiring a viewer' ),
   ( 'DIRECT',    'direct',          'no intermediation required' ),
   ( 'VIDEO',     'video',           'electronic moving picture' );


-- ---------------------------------------------------------------------
-- Describes the item "carrier," the physical object or device that
-- embodies the information.  This is a sparse combination of
-- Content_Type and Media_Type.
--
CREATE TABLE IF NOT EXISTS `Carrier_Type` (
   Content_Type_ID  CHAR(8),
   Media_Type_ID    CHAR(8),
   ID               CHAR(8) NOT NULL,
   name             VARCHAR(32),
   description      VARCHAR(128),

   UNIQUE INDEX ( `Content_Type_ID`, `Media_Type_ID`, `ID` ),

   FOREIGN KEY ( `Content_Type_ID` ) REFERENCES `Content_Type` ( `ID` )
      ON DELETE CASCADE
      ON UPDATE CASCADE,

   FOREIGN KEY ( `Media_Type_ID` ) REFERENCES `Media_Type` ( `ID` )
      ON DELETE CASCADE
      ON UPDATE CASCADE
) ENGINE = `InnoDB`;

INSERT INTO `Carrier_Type` VALUES

--   Content    Media       Carrier     (short) Name           Description

   ( 'CART',    NULL,       'CGLOBE',   'celestial globe',     'spherical representation of the celestial sky' ),
   ( 'CART',    NULL,       'EGLOBE',   'Earth globe',         'spherical representation of the Earth' ),
   ( 'CART',    NULL,       'PGLOGE',   'planetary globe',     'spherical representation of a planet(oid) other than Earth' ),
   ( 'CART',    NULL,       'ATLAS',    'atlas',               'codex-bound collection of maps' ),
   ( 'CART',    NULL,       'DIAGRAM',  'diagram',             'non-representational map' ),
   ( 'CART',    NULL,       'MAP',      'map',                 'representational map' ),
   ( 'CART',    NULL,       'MODEL',    'model',               'three-dimensional representation' ),
   ( 'CART',    NULL,       'PROFILE',  'profile',             '?' ),
   ( 'CART',    NULL,       'SATPIC',   'remote-sensing',      'satellite photograph' ),
   ( 'CART',    NULL,       'SECTION',  'section',             'transverse view of geography?' ),
   ( 'CART',    NULL,       'VIEW',     'view',                'non-photographic non-artistic rendering of geography?' ),

   ( 'ELEC',    NULL,       'SSCART',   'chip cartridge',      'solid-state removable storage, USB stick, etc.' ),
   ( 'ELEC',    NULL,       'OPTCART',  'optical catridge',    'optical ROM in cartridge carrier' ),
   ( 'ELEC',    NULL,       'MAGDISK',  'magnetic disk',       'fixed or removable magnetic disk' ),
   ( 'ELEC',    NULL,       'OPTDISK',  'optical disk',        'CD, CD-ROM, DVD, DVD-ROM, BluRay, etc.' ),
   ( 'ELEC',    NULL,       'REMOTE',   'remote',              'Accessible via public or private URL' ),
   ( 'ELEC',    NULL,       'ETAPCART', 'tape cartridge',      'magnetic or perforated tape in cartridge' ),
   ( 'ELEC',    NULL,       'ETAPCASS', 'tape cassette',       'magnetic or perforated tape in cassette' ),
   ( 'ELEC',    NULL,       'ETAPREEL', 'tape reel',           'magnetic or perforated tape on reel' ),

   ( NULL,      'MICFORM',  'APERCARD', 'aperture card',       '?' ),
   ( NULL,      'MICFORM',  'FICHE',    'microfiche',          'microfiche' ),
   ( NULL,      'MICFORM',  'FICHCASS', 'fiche cassette',      'microfiche cassette' ),
   ( NULL,      'MICFORM',  'FILMCASS', 'film cassette',       'microfilm cassette' ),
   ( NULL,      'MICFORM',  'FILMCART', 'film cartridge',      'microfilm cartridge' ),
   ( NULL,      'MICFORM',  'FILMREEL', 'film reel',           'microfilm reel' ),
   ( NULL,      'MICFORM',  'MICOPAQ',  'opaque',              'opaque micro format' ),

   ( NULL,      'MICSCOPE', 'MSLIDE',   'slide',               'microscopic slide' ),
   ( NULL,      'MICSCOPE', 'OTHER',    'other',               'other microscope media' ),

   ( 'MOVING',  NULL,       'FILMCART', 'film cartridge',      'film cartridge' ),
   ( 'MOVING',  NULL,       'FILMCASS', 'film cassette',       'film cassette' ),
   ( 'MOVING',  NULL,       'FILMREEL', 'film reel',           'film reel' ),
   ( 'MOVING',  NULL,       'VIDCART',  'videocartridge',      'video cartridge' ),
   ( 'MOVING',  NULL,       'VIDCASS',  'videocassette',       'video cassette, VHS, etc.' ),
   ( 'MOVING',  NULL,       'VIDDISC',  'videodisc',           'laser, DVD, BluRay, etc.' ),
   ( 'MOVING',  NULL,       'VIDREEL',   'videoreel',          'videotape reel' ),

   ( 'VISUAL',  NULL,       'CHART',    'chart',               'chart' ),
   ( 'VISUAL',  NULL,       'COLLAGE',  'collage',             'collage' ),
   ( 'VISUAL',  NULL,       'DRAWING',  'drawing',             'drawing' ),
   ( 'VISUAL',  NULL,       'FLSHCARD', 'flash card',          'flash card' ),
   ( 'VISUAL',  NULL,       'PAINTG',   'painting',            'painting' ),
   ( 'VISUAL',  NULL,       'PHTPRINT', 'photoprint',          'photomechanical print' ),
   ( 'VISUAL',  NULL,       'PHTNEG',   'negative',            'photographic negative' ),
   ( 'VISUAL',  NULL,       'PICTURE',  'picture',             'picture' ),
   ( 'VISUAL',  NULL,       'PRINT',    'print',               'print' ),
   ( 'VISUAL',  NULL,       'TECHDRAW', 'tech. drawing',       'technical drawing' ),

   ( 'PERF',    NULL,       'MUSIC',    'music',               'music' ),
   ( 'PERF',    NULL,       'DANCE',    'dance',               'dance' ),
   ( 'PERF',    NULL,       'OTHER',    'other',               'other' ),

   ( NULL,      'PROJ',     'FILMSLIP', 'filmslip',            'filmslip' ),
   ( NULL,      'PROJ',     'FILMCART', 'filmstrip cartridge', 'filmstrip cartridge' ),
   ( NULL,      'PROJ',     'FILMREEL', 'filmstrip roll',      'filmstrip roll' ),
   ( NULL,      'PROJ',     'FILMOTHR', 'filmstrip other',     'other filmstrip type' ),
   ( NULL,      'PROJ',     'PHTSLIDE', 'slide',               'photographic slide' ),
   ( NULL,      'PROJ',     'TRANSP',   'transparency',        'transparency' ),

   ( 'SOUND',   'AUDIO',    'AUDCYL',   'cylinder',            'phonograph cylinder' ),
   ( 'SOUND',   'AUDIO',    'AUDROLL',  'roll',                'encoded roll, e.g. for music automaton' ),
   ( 'SOUND',   'AUDIO',    'AUDCART',  'sound cartridge',     'audiotape cartridge' ),
   ( 'SOUND',   'AUDIO',    'AUDCASS',  'sound cassette',      'audiotape cassette' ),
   ( 'SOUND',   'AUDIO',    'AUDDISC',  'sound disc',          'phonographic disc' ),
   ( 'SOUND',   'AUDIO',    'AUDREEL',  'sound reel',          'audiotape reel' ),
   ( 'SOUND',   'AUDIO',    'AUDTRACK', 'sound track',         'optical film soundtrack' ),
   ( 'SOUND',   'AUDIO',    'AUDWIRE',  'wire',                'magnetic wire' ),

   ( 'SPOKEN',  'AUDIO',    'AUDCYL',   'cylinder',            'phonograph cylinder' ),
   ( 'SPOKEN',  'AUDIO',    'AUDCART',  'sound cartridge',     'audiotape cartridge' ),
   ( 'SPOKEN',  'AUDIO',    'AUDCASS',  'sound cassette',      'audiotape cassette' ),
   ( 'SPOKEN',  'AUDIO',    'AUDDISC',  'sound disc',          'phonographic disc' ),
   ( 'SPOKEN',  'AUDIO',    'AUDREEL',  'sound reel',          'audiotape reel' ),
   ( 'SPOKEN',  'AUDIO',    'AUDTRACK', 'sound track',         'optical film soundtrack' ),
   ( 'SPOKEN',  'AUDIO',    'AUDWIRE',  'wire',                'magnetic wire' ),

   ( NULL,      'STEREO',   'STCARD',   'card',                'stereoscope card' ),
   ( NULL,      'STEREO',   'STDISC',   'disc',                'stereo disc, e.g. for Viewmaster' ),
   ( NULL,      'STEREO',   'ANAGLYPH', 'anaglyph',            'red-blue anaglyph' ),

   ( 'TACTILE', NULL,       'BRAILLE',  'braille',             'Braille embossing' ),
   ( 'TACTILE', NULL,       'MOON',     'moon',                'Moon embossing' ),
   ( 'TACTILE', NULL,       'TACTILE',  'tactile',             'purely tactile; no writing system' ),
   ( 'TACTILE', NULL,       'OTHER',    'other',               'other' ),

   ( 'TEXT',    NULL,       'CODEX',    'codex',               'Bound book' ),
   ( 'TEXT',    NULL,       'ROLL',     'roll',                'Roll' ),
   ( 'TEXT',    NULL,       'SHEET',    'sheet',               'Single sheet' ),
   ( 'TEXT',    NULL,       'VOLUME',   'volume',              'Rebound volume' ),
   ( 'TEXT',    NULL,       'BINDER',   'binder',              'Loose-leaf binder' );
