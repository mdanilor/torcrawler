-- MySQL Script generated by MySQL Workbench
-- Sat 24 Jun 2017 07:01:29 PM BRT
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema torcrawler
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema torcrawler
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `torcrawler` DEFAULT CHARACTER SET utf8 ;
USE `torcrawler` ;

-- -----------------------------------------------------
-- Table `torcrawler`.`HiddenServices`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `torcrawler`.`HiddenServices` (
  `Id` INT NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(2048) NULL,
  `Url` VARCHAR(2048) NOT NULL,
  `Status` INT NOT NULL,
  `FirstScan` DATETIME NULL,
  `LatestScan` DATETIME NULL,
  `LastSeenOnline` DATETIME NULL,
  `ResponsibleThread` BIGINT NULL,
  PRIMARY KEY (`Id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `torcrawler`.`Links`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `torcrawler`.`Links` (
  `Id` INT NOT NULL AUTO_INCREMENT,
  `Url` VARCHAR(2048) NOT NULL,
  `Title` VARCHAR(2048) NULL,
  `CreatedOn` DATETIME NOT NULL,
  `HiddenServiceId` INT NULL,
  `ResourcePath` VARCHAR(2048) NULL,
  `IsIndex` TINYINT(1) NULL,
  `HTMLHash` VARCHAR(32) NULL,
  `Status` SMALLINT NOT NULL,
  `Header` VARCHAR(4096) NULL,
  PRIMARY KEY (`Id`),
  INDEX `HiddenService_Link_FK_idx` (`HiddenServiceId` ASC),
  CONSTRAINT `HiddenService_Link_FK`
    FOREIGN KEY (`HiddenServiceId`)
    REFERENCES `torcrawler`.`HiddenServices` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;