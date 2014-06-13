DROP DATABASE "spacedb";
CREATE DATABASE "spacedb"
/*  WITH OWNER "postgres"*/;
/*!40100 DEFAULT CHARACTER SET utf8 */
\c spacedb
-- MySQL dump 10.13  Distrib 5.6.12, for Win64 (x86_64)
--
-- Host: localhost    Database: spacedb
-- ------------------------------------------------------
-- Server version	5.6.12

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table "attribution"
--
DROP TYPE IF EXISTS unit_length;
CREATE TYPE unit_length AS ENUM ('METERS','FEET');

DROP TYPE IF EXISTS unit_length_angle;
CREATE TYPE unit_length_angle AS ENUM ('METERS','FEET', 'DEG', 'RAD');

DROP TYPE IF EXISTS coordinate_system;
CREATE TYPE coordinate_system AS ENUM ('LVCS','Cartesian');

DROP TYPE IF EXISTS transformation_type;
CREATE TYPE transformation_type AS ENUM ('Cartesian','Similarity','Geographic');

DROP TYPE IF EXISTS pixel_format;
CREATE TYPE pixel_format AS ENUM ('FLOAT','DOUBLE','BYTE','SHORT');

DROP TYPE IF EXISTS event_type;
CREATE TYPE event_type AS ENUM ('REFERENCE','PRIMITIVE','IMAGE','PERSON','AUTO','BUS','TRAIN','MODEL');

DROP TYPE IF EXISTS event_order;
CREATE TYPE event_order AS ENUM ('LEQ','GEQ','SHIFT');

DROP TYPE IF EXISTS datum_type;
CREATE TYPE datum_type AS ENUM ('WGS84','UTM');

DROP TYPE IF EXISTS model_type;
CREATE TYPE model_type AS ENUM ('VOLUMETRIC','POLYHEDRAL','PLANE','CYLINDER','POINTCLOUD');

DROP TABLE IF EXISTS "attribution";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "attribution" (
  "AttributeId" int4 NOT NULL,
  "Category" varchar(45) DEFAULT NULL,
  "Topic" varchar(45) DEFAULT NULL,
  "Attribute" varchar(45) DEFAULT NULL,
  PRIMARY KEY ("AttributeId"),
  CONSTRAINT "fk_Attribution_Event1" FOREIGN KEY ("AttributeId") REFERENCES "event" ("EventId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "event"
--

DROP TABLE IF EXISTS "event";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "event" (
  "EventId" serial,
  "EventType" event_type NOT NULL,
  "EventName" varchar(128) DEFAULT 'no name',
  "EventDescription" text,
  PRIMARY KEY ("EventId")
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "image"
--

DROP TABLE IF EXISTS "image";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "image" (
  "ImageName" varchar(128) NOT NULL,
  "FileFormat" varchar(4) NOT NULL,
  "PixelFormat" pixel_format DEFAULT NULL,
  "ImageWidth" int4 NOT NULL,
  "ImageHeight" int4 NOT NULL,
  "NColorBands" int4 NOT NULL,
  "ImageURL" text NOT NULL,
  "ImageId" int4 NOT NULL,
  PRIMARY KEY ("ImageId"),
  CONSTRAINT "ImageId" FOREIGN KEY ("ImageId") REFERENCES "event" ("EventId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "camera"
--

DROP TABLE IF EXISTS "camera";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "camera" (
  "FocalLengthU" double precision NOT NULL,
  "FocalLengthV" double precision NOT NULL,
  "PrincipalPointU" double precision NOT NULL,
  "PrincipalPointV" double precision NOT NULL,
  "CoordinateSystem_CSId" int4 NOT NULL,
  "ImageId" int4 NOT NULL,
  PRIMARY KEY ("CoordinateSystem_CSId","ImageId"),
--  KEY "fk_Camera_Image1_idx" ("ImageId"),
  CONSTRAINT "fk_Camera_CoordinateSystem1" FOREIGN KEY ("CoordinateSystem_CSId") REFERENCES "coordinatesystem" ("CSId") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_Camera_Image1" FOREIGN KEY ("ImageId") REFERENCES "image" ("ImageId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "cartesiancoordinatesystem"
--

DROP TABLE IF EXISTS "cartesiancoordinatesystem";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "cartesiancoordinatesystem" (
  "XUnit" unit_length NOT NULL DEFAULT 'METERS',
  "YUnit" unit_length  NOT NULL DEFAULT 'METERS',
  "ZUnit" unit_length  NOT NULL DEFAULT 'METERS',
  "CoordinateSystem_CSId" int4 NOT NULL,
  PRIMARY KEY ("CoordinateSystem_CSId"),
  CONSTRAINT "fk_CartesianCoordinateSystem_CoordinateSystem1" FOREIGN KEY ("CoordinateSystem_CSId") REFERENCES "coordinatesystem" ("CSId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "cartesiantransform"
--

DROP TABLE IF EXISTS "cartesiantransform";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "cartesiantransform" (
  "RodriguesX" double precision NOT NULL,
  "RodriguesY" double precision NOT NULL,
  "RodriguesZ" double precision NOT NULL,
  "TranslationX" double precision NOT NULL,
  "TranslationY" double precision NOT NULL,
  "TranslationZ" double precision NOT NULL,
  "CoordinateTransform_TransformId" int4 NOT NULL,
  PRIMARY KEY ("CoordinateTransform_TransformId"),
  CONSTRAINT "fk_CartesianTransform_CoordinateTransform1" FOREIGN KEY ("CoordinateTransform_TransformId") REFERENCES "coordinatetransform" ("TransformId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view "carttransview"
--

DROP TABLE IF EXISTS "carttransview";
/*!50001 DROP VIEW IF EXISTS "carttransview"*/;
-- SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE "carttransview" (
  "CS0Id" tinyint NOT NULL,
  "CS1Id" tinyint NOT NULL,
  "TransformId" tinyint NOT NULL,
  "RodriguesX" tinyint NOT NULL,
  "RodriguesY" tinyint NOT NULL,
  "RodriguesZ" tinyint NOT NULL,
  "TranslationX" tinyint NOT NULL,
  "TranslationY" tinyint NOT NULL,
  "TranslationZ" tinyint NOT NULL
) ENGINE=MyISAM */;
-- SET character_set_client = @saved_cs_client;

--
-- Table structure for table "coordinatesystem"
--

DROP TABLE IF EXISTS "coordinatesystem";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "coordinatesystem" (
  "CSId" serial,
  "CSType" coordinate_system NOT NULL DEFAULT 'Cartesian',
  PRIMARY KEY ("CSId")
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "coordinatetransform"
--

DROP TABLE IF EXISTS "coordinatetransform";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "coordinatetransform" (
  "TransformId" serial,
  "CS0Id" int4 NOT NULL,
  "CS1Id" int4 NOT NULL,
  "TransformType" transformation_type NOT NULL DEFAULT 'Cartesian',
  PRIMARY KEY ("TransformId"),
--  KEY "fk_CoordinateTransform_CoordinateSystem1_idx" ("CS0Id"),
--  KEY "fk_CoordinateTransform_CoordinateSystem2_idx" ("CS1Id"),
  CONSTRAINT "fk_CoordinateTransform_CoordinateSystem1" FOREIGN KEY ("CS0Id") REFERENCES "coordinatesystem" ("CSId") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_CoordinateTransform_CoordinateSystem2" FOREIGN KEY ("CS1Id") REFERENCES "coordinatesystem" ("CSId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "depthmap"
--

DROP TABLE IF EXISTS "depthmap";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "depthmap" (
  "FileFormat" varchar(4) NOT NULL,
  "PixelFormat" pixel_format NOT NULL,
  "DepthUrl" text,
  "ImageId" int4 NOT NULL,
  PRIMARY KEY ("ImageId"),
--  KEY "fk_DepthMap_Image1_idx" ("ImageId"),
  CONSTRAINT "fk_DepthMap_Image1" FOREIGN KEY ("ImageId") REFERENCES "image" ("ImageId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "eventorderrelation"
--

DROP TABLE IF EXISTS "eventorderrelation";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "eventorderrelation" (
  "OrderType" event_order DEFAULT NULL,
  "TimeDiffMsec" int4 DEFAULT NULL,
  "Name" varchar(45) DEFAULT NULL,
  "EventIdFrom" int4 NOT NULL,
  "EventIdTo" int4 NOT NULL,
--  KEY "fk_EventOrderRelation_Event1_idx" ("EventIdFrom"),
--  KEY "fk_EventOrderRelation_Event2_idx" ("EventIdTo"),
  CONSTRAINT "fk_EventOrderRelation_Event1" FOREIGN KEY ("EventIdFrom") REFERENCES "event" ("EventId") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_EventOrderRelation_Event2" FOREIGN KEY ("EventIdTo") REFERENCES "event" ("EventId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "eventtimeinterval"
--

DROP TABLE IF EXISTS "eventtimeinterval";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "eventtimeinterval" (
  "IntervalId" serial,
  "EventId" int4 DEFAULT NULL,
  "StartTime" timestamp NOT NULL,
  "StartMsec" int4 DEFAULT '0',
  "EndTime" timestamp NOT NULL,
  "EndMsec" int4 DEFAULT '0',
  PRIMARY KEY ("IntervalId"),
--  KEY "fk_EventTimeInterval_Event1_idx" ("EventId"),
  CONSTRAINT "fk_EventTimeInterval_Event1" FOREIGN KEY ("EventId") REFERENCES "event" ("EventId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "eventtimestamp"
--

DROP TABLE IF EXISTS "eventtimestamp";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "eventtimestamp" (
  "TimeId" serial,
  "EventId" int4 DEFAULT NULL,
  "Time" timestamp NOT NULL,
  "TimeMsec" int4 DEFAULT '0',
  PRIMARY KEY ("TimeId"),
--  KEY "fk_EventTimeStamp_Event1_idx" ("EventId"),
  CONSTRAINT "fk_EventTimeStamp_Event1" FOREIGN KEY ("EventId") REFERENCES "event" ("EventId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view "imageview"
--

DROP TABLE IF EXISTS "imageview";
/*!50001 DROP VIEW IF EXISTS "imageview"*/;
--SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE "imageview" (
  "EventId" tinyint NOT NULL,
  "EventDescription" tinyint NOT NULL,
  "ImageName" tinyint NOT NULL,
  "FileFormat" tinyint NOT NULL,
  "PixelFormat" tinyint NOT NULL,
  "ImageWidth" tinyint NOT NULL,
  "ImageHeight" tinyint NOT NULL,
  "NColorBands" tinyint NOT NULL,
  "ImageData" tinyint NOT NULL
) ENGINE=MyISAM */;
--SET character_set_client = @saved_cs_client;

--
-- Table structure for table "localverticalcoordinatesystem"
--

DROP TABLE IF EXISTS "localverticalcoordinatesystem";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "localverticalcoordinatesystem" (
  "CSType" datum_type DEFAULT 'WGS84',
  "XUnit" unit_length_angle DEFAULT 'DEG',
  "YUnit" unit_length_angle DEFAULT 'DEG',
  "ZUnit" unit_length DEFAULT NULL,
  "OriginX" double precision DEFAULT '0',
  "OriginY" double precision DEFAULT '0',
  "OriginZ" double precision DEFAULT '0',
  "CoordinateSystem_CSId" serial,
  PRIMARY KEY ("CoordinateSystem_CSId"),
  CONSTRAINT "fk_LocalVerticalCoordinateSystem_CoordinateSystem1" FOREIGN KEY ("CoordinateSystem_CSId") REFERENCES "coordinatesystem" ("CSId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "model3d"
--

DROP TABLE IF EXISTS "model3d";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "model3d" (
  "ModelId" serial,
  "Type" model_type DEFAULT NULL,
  "CoordinateSystem_CSId" int4 NOT NULL,
  "Site_SiteId" int4 DEFAULT NULL,
  PRIMARY KEY ("ModelId","CoordinateSystem_CSId"),
--  KEY "fk_Model3D_CoordinateSystem1_idx" ("CoordinateSystem_CSId"),
--  KEY "fk_Model3D_Site1_idx" ("Site_SiteId"),
  CONSTRAINT "fk_Model3D_CoordinateSystem1" FOREIGN KEY ("CoordinateSystem_CSId") REFERENCES "coordinatesystem" ("CSId") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_Model3D_Event1" FOREIGN KEY ("ModelId") REFERENCES "event" ("EventId") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_Model3D_Site1" FOREIGN KEY ("Site_SiteId") REFERENCES "site" ("SiteId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "modelimages"
--

DROP TABLE IF EXISTS "modelimages";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "modelimages" (
  "Model3D_ModelId" int4 NOT NULL,
  "Image_ImageId" int4 NOT NULL,
--  KEY "fk_ModelImages_Model3D1_idx" ("Model3D_ModelId"),
  CONSTRAINT "fk_ModelImages_Model3D1" FOREIGN KEY ("Model3D_ModelId") REFERENCES "model3d" ("ModelId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "referenceevent"
--

DROP TABLE IF EXISTS "referenceevent";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "referenceevent" (
  "RefId" int4 NOT NULL,
  "GMTOffset" int4 DEFAULT NULL,
  "BaseTime" timestamp NOT NULL,
  "RefCSId" int4 NOT NULL,
--  KEY "fk_RefEvent_Event1_idx" ("RefId"),
--  KEY "fk_RefEvent_CoordinateSystem1_idx" ("RefCSId"),
  CONSTRAINT "fk_RefEvent_CoordinateSystem1" FOREIGN KEY ("RefCSId") REFERENCES "coordinatesystem" ("CSId") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_RefEvent_Event1" FOREIGN KEY ("RefId") REFERENCES "event" ("EventId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "similaritytransform"
--

DROP TABLE IF EXISTS "similaritytransform";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "similaritytransform" (
  "Scale" double precision NOT NULL,
  "RodriguesX" double precision NOT NULL,
  "RodriguesY" double precision NOT NULL,
  "RodriguesZ" double precision NOT NULL,
  "TranslationX" double precision NOT NULL,
  "TranslationY" double precision NOT NULL,
  "TranslationZ" double precision NOT NULL,
  "CoordinateTransform_TransformId" int4 NOT NULL,
  PRIMARY KEY ("CoordinateTransform_TransformId"),
  CONSTRAINT "fk_SimilarityTransform_CoordinateTransform1" FOREIGN KEY ("CoordinateTransform_TransformId") REFERENCES "coordinatetransform" ("TransformId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "site"
--

DROP TABLE IF EXISTS "site";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "site" (
  "SiteId" int4 NOT NULL,
  "SiteName" varchar(45) NOT NULL,
--  KEY "fk_Site_ReferenceEvent1_idx" ("SiteId"),
  CONSTRAINT "fk_Site_ReferenceEvent1" FOREIGN KEY ("SiteId") REFERENCES "referenceevent" ("RefId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "siteevents"
--

DROP TABLE IF EXISTS "siteevents";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "siteevents" (
  "Site_SiteId" int4 NOT NULL,
  "EventId" int4 DEFAULT NULL,
--  KEY "fk_SiteEvents_Site1_idx" ("Site_SiteId"),
  CONSTRAINT "fk_SiteEvents_Site1" FOREIGN KEY ("Site_SiteId") REFERENCES "site" ("SiteId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view "siteeventview"
--

DROP TABLE IF EXISTS "siteeventview";
/*!50001 DROP VIEW IF EXISTS "siteeventview"*/;
--SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE "siteeventview" (
  "Site_SiteId" tinyint NOT NULL,
  "EventId" tinyint NOT NULL,
  "EventType" tinyint NOT NULL,
  "EventName" tinyint NOT NULL
) ENGINE=MyISAM */;
--SET character_set_client = @saved_cs_client;

--
-- Temporary table structure for view "siteview"
--

DROP TABLE IF EXISTS "siteview";
/*!50001 DROP VIEW IF EXISTS "siteview"*/;
--SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE "siteview" (
  "EventId" tinyint NOT NULL,
  "EventDescription" tinyint NOT NULL,
  "GMTOffset" tinyint NOT NULL,
  "BaseTime" tinyint NOT NULL,
  "RefCSId" tinyint NOT NULL,
  "SiteName" tinyint NOT NULL
) ENGINE=MyISAM */;
--SET character_set_client = @saved_cs_client;

--
-- Table structure for table "viewoverlap"
--

DROP TABLE IF EXISTS "viewoverlap";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "viewoverlap" (
  "ImageId0" int4 NOT NULL,
  "ImageId1" int4 NOT NULL,
  "NCorrespondences" int4 DEFAULT '0',
  "OverlapFraction" float DEFAULT '0',
--  KEY "fk_ViewOverlap_Image1_idx" ("ImageId0"),
--  KEY "fk_ViewOverlap_Image2_idx" ("ImageId1"),
  CONSTRAINT "fk_ViewOverlap_Image1" FOREIGN KEY ("ImageId0") REFERENCES "image" ("ImageId") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "fk_ViewOverlap_Image2" FOREIGN KEY ("ImageId1") REFERENCES "image" ("ImageId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table "volumemodel"
--

DROP TABLE IF EXISTS "volumemodel";
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE "volumemodel" (
  "Model3D_ModelId" int4 NOT NULL,
  "FilePath" varchar(128) NOT NULL,
  "BoundingBoxXMin" double precision NOT NULL,
  "BoundingBoxYMin" double precision NOT NULL,
  "BoundingBoxZMin" double precision NOT NULL,
  "BoundingBoxXMax" double precision NOT NULL,
  "BoundingBoxYMax" double precision NOT NULL,
  "BoundingBoxZMax" double precision NOT NULL,
  PRIMARY KEY ("Model3D_ModelId"),
  CONSTRAINT "fk_VolumeModel_Model3D1" FOREIGN KEY ("Model3D_ModelId") REFERENCES "model3d" ("ModelId") ON DELETE NO ACTION ON UPDATE NO ACTION
);
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view "carttransview"
--

/*!50001 DROP TABLE IF EXISTS "carttransview"*/;
/*!50001 DROP VIEW IF EXISTS "carttransview"*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER="root"@"localhost" SQL SECURITY DEFINER */
/*!50001 VIEW "carttransview" AS select "coordinatetransform"."CS0Id" AS "CS0Id","coordinatetransform"."CS1Id" AS "CS1Id","coordinatetransform"."TransformId" AS "TransformId","cartesiantransform"."RodriguesX" AS "RodriguesX","cartesiantransform"."RodriguesY" AS "RodriguesY","cartesiantransform"."RodriguesZ" AS "RodriguesZ","cartesiantransform"."TranslationX" AS "TranslationX","cartesiantransform"."TranslationY" AS "TranslationY","cartesiantransform"."TranslationZ" AS "TranslationZ" from ("coordinatetransform" join "cartesiantransform" on(("coordinatetransform"."TransformId" = "cartesiantransform"."CoordinateTransform_TransformId"))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view "imageview"
--

/*!50001 DROP TABLE IF EXISTS "imageview"*/;
/*!50001 DROP VIEW IF EXISTS "imageview"*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER="root"@"localhost" SQL SECURITY DEFINER */
/*!50001 VIEW "imageview" AS select "event"."EventId" AS "EventId","event"."EventDescription" AS "EventDescription","image"."ImageName" AS "ImageName","image"."FileFormat" AS "FileFormat","image"."PixelFormat" AS "PixelFormat","image"."ImageWidth" AS "ImageWidth","image"."ImageHeight" AS "ImageHeight","image"."NColorBands" AS "NColorBands","image"."ImageData" AS "ImageData" from ("event" join "image" on(("event"."EventId" = "image"."ImageId"))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view "siteeventview"
--

/*!50001 DROP TABLE IF EXISTS "siteeventview"*/;
/*!50001 DROP VIEW IF EXISTS "siteeventview"*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER="root"@"localhost" SQL SECURITY DEFINER */
/*!50001 VIEW "siteeventview" AS select "siteevents"."Site_SiteId" AS "Site_SiteId","siteevents"."EventId" AS "EventId","event"."EventType" AS "EventType","event"."EventName" AS "EventName" from ("siteevents" join "event" on(("event"."EventId" = "siteevents"."EventId"))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view "siteview"
--

/*!50001 DROP TABLE IF EXISTS "siteview"*/;
/*!50001 DROP VIEW IF EXISTS "siteview"*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER="root"@"localhost" SQL SECURITY DEFINER */
/*!50001 VIEW "siteview" AS select "event"."EventId" AS "EventId","event"."EventDescription" AS "EventDescription","referenceevent"."GMTOffset" AS "GMTOffset","referenceevent"."BaseTime" AS "BaseTime","referenceevent"."RefCSId" AS "RefCSId","site"."SiteName" AS "SiteName" from (("event" join "referenceevent" on(("event"."EventId" = "referenceevent"."RefId"))) join "site" on(("event"."EventId" = "site"."SiteId"))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-05-27 16:02:52
