package database

import (
	"fmt"
	"log"
	"os"

	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func DB() *gorm.DB {

	// Load .env file
	err := godotenv.Load()
	if err != nil {
		log.Fatalf("Error loading .env file")
	}

	// Postgres credentials
	POSTGRES_DB := os.Getenv("POSTGRES_DB")
	POSTGRES_USER := os.Getenv("POSTGRES_USER")
	POSTGRES_PASSWORD := os.Getenv("POSTGRES_PASSWORD")
	POSTGRES_HOST := os.Getenv("POSTGRES_HOST")
	POSTGRES_PORT := os.Getenv("POSTGRES_PORT")

	// Connect to database
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		POSTGRES_HOST,
		POSTGRES_PORT,
		POSTGRES_USER,
		POSTGRES_PASSWORD,
		POSTGRES_DB,
	)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("Database connections error: %v", err)
	} else {
		fmt.Println("Connected to database...")
	}

	// Enable UUID extension
	db.Exec("CREATE EXTENSION IF NOT EXISTS pgcrypto")

	// Auto migrate models
	err = db.AutoMigrate(
		&JournalEntry{},
		&Account{},
		&Credit{},
		&Debit{},
	)

	if err != nil {
		log.Fatalf("failed to migrate database: %v", err)
	}

	return db
}
