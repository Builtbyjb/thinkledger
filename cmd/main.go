package main

import (
	"log"
	"os"

	"server/internal/handlers"
	"server/internal/middleware"

	"github.com/gofiber/fiber/v2"
	"github.com/joho/godotenv"
)

func main() {

	// Load .env file
	err := godotenv.Load()
	if err != nil {
		log.Fatalf("Error loading .env file")
	}

	// Get gemini api key
	GEMINI_API_KEY := os.Getenv("GEMINI_DEV_API_KEY")

	app := fiber.New()

	app.Use(
		middleware.Cors(),
		middleware.RateLimiter(),
		middleware.RequestTimer(),
	)

	app.Static("/static", "./static")

	// Connect to database and create database engine
	// db := database.DB()

	handler := &handlers.Handler{
		// DB:     db,
		ApiKey: GEMINI_API_KEY,
	}

	// health check
	app.Get("/ping", func(c *fiber.Ctx) error {
		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"ping": "pong!",
		})
	})

	// Web routes
	app.Get("/", handler.Index)
	app.Route("/support", func(route fiber.Router) {
		route.Get("/", handler.Support)
		route.Get("/bookkeeping", handler.SupportBookkeeping)
		route.Get("/financial-reports", handler.SupportFinancialReports)
		route.Get("/analytics-insights", handler.SupportAnalyticsInsights)
	}, "support.")
	app.Get("/privacy-policy", handler.PrivacyPolicy)
	app.Get("/terms-of-service", handler.TermsOfService)

	// Api routes
	v1 := app.Group("/api/v1")
	v1.Post("/chat", middleware.ChatAuth(), handler.HandleChat)

	// api.Get("/journal", handler.HandleJournal)
	// api.Get("/t-accounts", handler.HandleTAccount)
	// api.Get("/trial-balance", handler.HandleTrialBalance)

	log.Fatal(app.Listen("0.0.0.0:3000"))
}
