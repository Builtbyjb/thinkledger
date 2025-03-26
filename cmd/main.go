package main

import (
	"net/http"
	"os"

	"server/internal/database/redis"
	"server/internal/handlers"
	"server/internal/middleware"
	"server/internal/utils"

	"github.com/joho/godotenv"
	"github.com/labstack/echo/v4"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
)

func init() {
	// Load .env file
	godotenv.Load()
}

type healthRes struct {
	Ping string `json:"ping"`
	Env  string `json:"env"`
}

func main() {

	// Get gemini api key
	GEMINI_API_KEY := os.Getenv("GEMINI_DEV_API_KEY")

	app := echo.New()

	app.Use(middleware.Cors())
	app.Use(middleware.RequestTimer())
	app.Use(middleware.RateLimiter())
	app.Use(middleware.Recover())

	app.Static("/static", "./static")

	// Create redis client
	redisClient := redis.GetRedisClient()

	// OAuth2 configuration
	var oAuthConfig = &oauth2.Config{
		ClientID:     os.Getenv("GOOGLE_CLIENT_ID"),
		ClientSecret: os.Getenv("GOOGLE_CLIENT_SECRET"),
		RedirectURL:  os.Getenv("GOOGLE_REDIRECT_URL"),
		Scopes: []string{
			"https://www.googleapis.com/auth/userinfo.email",
			"https://www.googleapis.com/auth/userinfo.profile",
		},
		Endpoint: google.Endpoint,
	}

	// For authentication middleware
	authConfig := utils.AuthConfig{
		OAuth2Config: oAuthConfig,
		RedisClient:  redisClient,
	}

	// Dependency injection between routes
	handler := &handlers.Handler{
		// DB:     db,
		OAuthConfig: oAuthConfig,
		ApiKey:      GEMINI_API_KEY,
		RedisClient: redisClient,
	}

	// health check
	app.GET("/ping", func(c echo.Context) error {
		envCheck := os.Getenv("ENV_CHECK")

		healthCheck := &healthRes{
			Ping: "Pong!!",
			Env:  envCheck,
		}
		return c.JSON(http.StatusOK, healthCheck)
	})

	// Web routes
	app.GET("/", handler.Index)

	app.GET("/support", handler.Support)
	app.GET("/support/bookkeeping", handler.SupportBookkeeping)
	app.GET("/support/financial-reports", handler.SupportFinancialReports)
	app.GET("/support/analytics-insights", handler.SupportAnalyticsInsights)

	app.GET("/privacy-policy", handler.PrivacyPolicy)
	app.GET("/terms-of-service", handler.TermsOfService)
	app.POST("/join-waitlist", handler.JoinWaitlist)
	app.GET("/sign-in", handler.SignIn)
	app.GET("/log-out", handler.HandleLogout)

	// Authentication routes
	app.GET("/auth-sign-in", handler.HandleSignInAuth)
	app.GET("/auth/google/callback", handler.HandleCallbackAuth)

	// Protected web routes
	protected := app.Group("", middleware.AuthRoutes(authConfig))
	protected.GET("/home", handler.Home)

	// Not found (404) handler
	app.GET("*", handler.NotFound)

	// Api routes
	// v1 := app.Group("/api/v1")
	// v1.POST("/chat", handler.HandleChat)

	// api.Get("/journal", handler.HandleJournal)
	// api.Get("/t-accounts", handler.HandleTAccount)
	// api.Get("/trial-balance", handler.HandleTrialBalance)

	app.Logger.Fatal(app.Start(":3000"))
}
