package main

import (
	"os"

	"server/internal/database/redis"
	"server/internal/handlers"
	"server/internal/middleware"
	"server/internal/utils"

	"github.com/joho/godotenv"
	"github.com/labstack/echo/v4"
	"github.com/plaid/plaid-go/plaid"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
)

func init() {
	// Load .env file
	godotenv.Load()
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
	oAuthConfig := &oauth2.Config{
		ClientID:     os.Getenv("GOOGLE_CLIENT_ID"),
		ClientSecret: os.Getenv("GOOGLE_CLIENT_SECRET"),
		RedirectURL:  os.Getenv("GOOGLE_REDIRECT_URL"),
		Scopes: []string{
			"https://www.googleapis.com/auth/userinfo.email",
			"https://www.googleapis.com/auth/userinfo.profile",
		},
		Endpoint: google.Endpoint,
	}

	// Plaid configuration
	configuration := plaid.NewConfiguration()
	configuration.AddDefaultHeader("PLAID-CLIENT-ID", os.Getenv("PLAID_CLIENT_ID"))
	configuration.AddDefaultHeader("PLAID-SECRET", os.Getenv("PLAID_CLIENT_SECRET"))
	configuration.UseEnvironment(plaid.Sandbox)
	plaidClient := plaid.NewAPIClient(configuration)

	// For middleware authentication
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
		PlaidClient: plaidClient,
	}

	// health check
	app.GET("/ping", func(c echo.Context) error {
		envCheck := os.Getenv("ENV_CHECK")

		return c.JSON(200, map[string]string{
			"ping": "pong!!",
			"env":  envCheck,
		})
	})

	// Web routes
	app.GET("/", handler.Index)

	// Routes that appear when a user is authenticated and unauthenticated
	dynamic := app.Group("", middleware.SetUserInfo(redisClient))
	dynamic.GET("/support", handler.Support)
	dynamic.GET("/support/bookkeeping", handler.SupportBookkeeping)
	dynamic.GET("/support/financial-reports", handler.SupportFinancialReports)
	dynamic.GET("/support/analytics-insights", handler.SupportAnalyticsInsights)
	dynamic.GET("/privacy-policy", handler.PrivacyPolicy)
	dynamic.GET("/terms-of-service", handler.TermsOfService)

	app.POST("/join-waitlist", handler.JoinWaitlist)

	app.GET("/sign-in", handler.SignIn)
	app.GET("/sign-out", handler.HandleSignout)

	// Authentication routes
	app.GET("/auth-sign-in", handler.HandleSignInAuth)
	app.GET("/auth/google/callback", handler.HandleGoogleCallbackAuth)

	// Protected web routes
	protected := app.Group("", middleware.AuthRoutes(authConfig))
	protected.GET("/home", handler.Home)
	protected.GET("/banking", handler.Banking)
	protected.GET("/plaid-link-token", handler.HandlePlaidLinkToken)
	protected.POST("/plaid-access-token", handler.HandlePlaidAccessToken)

	app.POST("/plaid-webhooks", handler.HandlePlaidWebhooks)
	app.GET("auth/plaid/callback", handler.HandlePlaidCallbackAuth)

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
