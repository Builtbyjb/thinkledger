package handlers

import (
	"encoding/json"
	"log"
	"net/http"
	"server/internal/database/postgres"
	"server/internal/utils"
	"time"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

func (h *Handler) GoogleSignInCallback(c echo.Context) error {
	ctx := c.Request().Context()

	// Verify state to prevent CSRF
	cookie, err := c.Cookie("state")
	if err != nil || cookie.Value != c.QueryParam("state") {
		log.Println(err)
		return c.String(400, "Invalid state parameter")
	}

	// Get google oauth2 token
	token, err := h.SignInAuthConfig.Exchange(ctx, c.QueryParam("code"))
	if err != nil {
		log.Println(err)
		return c.String(500, "Token exchange failed: "+err.Error())
	}

	// Generate authentication id
	sessionID := uuid.New().String()

	// Use the access token to get information about the user trying signing in
	userInfo, err := utils.GetUserInfo(token.AccessToken, h.SignInAuthConfig)
	if err != nil {
		log.Print(err)
		c.String(500, "Failed to get user info")
	}

	userID := userInfo.Sub

	var user postgres.User
	result := h.DB.Where("id = ?", userID).Find(&user)
	if result.Error != nil {
		log.Println("Database error")
		c.String(500, "Internal server error")
	}

	if result.RowsAffected == 0 {
		// Save new newUser, if no newUser was found
		newUser := postgres.User{
			ID:         userInfo.Sub,
			Email:      userInfo.Email,
			Name:       userInfo.Name,
			GivenName:  userInfo.GivenName,
			FamilyName: userInfo.FamilyName,
			Picture:    userInfo.Picture,
			Locale:     userInfo.Locale,
		}

		result := h.DB.Create(&newUser)
		if result.Error != nil {
			log.Println(result.Error)
			c.String(500, "Failed to save new user")
		}
		if err := utils.SaveUserSignInToken(h.RedisClient, token, userID); err != nil {
			log.Println(err)
			c.String(500, "Internal server error")
		}
	} else {
		if err := utils.SaveUserSignInToken(h.RedisClient, token, userID); err != nil {
			log.Println(err)
			c.String(500, "Internal server error")
		}
		h.DB.Save(&user)
	}

	// TODO: use goroutines
	// Set redis expiration date
	expiration := time.Duration(24 * time.Hour)

	if err := h.RedisClient.Set(ctx, sessionID, userInfo.Sub, expiration).Err(); err != nil {
		log.Println(err)
		return c.String(500, "Failed to save userID: "+err.Error())
	}

	// Save user access token
	userAccessToken := "signInAccessToken:" + userInfo.Sub
	if err := h.RedisClient.Set(ctx, userAccessToken, token.AccessToken, expiration).Err(); err != nil {
		log.Println(err)
		return c.String(500, "Failed to save token: "+err.Error())
	}

	// Save username
	username := "username:" + userInfo.Sub
	if err := h.RedisClient.Set(ctx, username, userInfo.Name, expiration).Err(); err != nil {
		log.Println(err)
		return c.String(500, "Failed to save username: "+err.Error())
	}

	// Set user authentication cookie
	c.SetCookie(&http.Cookie{
		Name:     "session_id",
		Value:    sessionID,
		HttpOnly: true,
		Path:     "/",
		Secure:   true,
		SameSite: http.SameSiteLaxMode,
		Expires:  time.Now().Add(24 * time.Hour),
	})

	return c.Redirect(307, "/home")
}

func (h *Handler) GoogleServiceCallback(c echo.Context) error {
	ctx := c.Request().Context()

	serviceCookie, err := c.Request().Cookie("service_state")
	if err != nil || serviceCookie.Value != c.QueryParam("state") {
		log.Println(err)
		c.String(500, "Invalid state parameter")
	}

	sessionCookie, err := c.Request().Cookie("session_id")
	if err != nil || sessionCookie.Value == "" {
		log.Println(err)
	}

	sessionID := sessionCookie.Value

	token, err := h.ServiceAuthConfig.Exchange(ctx, c.QueryParam("code"))
	if err != nil {
		log.Println(err)
		c.String(500, "Failed to get google token")
	}

	userID, err := h.RedisClient.Get(ctx, sessionID).Result()
	if err != nil {
		log.Println(err.Error())
		c.String(500, "Failed to get userID")
	}

	tokenBytes, err := json.Marshal(token)
	if err != nil {
		log.Println(err)
		c.String(500, "Failed to marshal token")
	}

	serviceToken := "serviceToken:" + userID
	if err := h.RedisClient.Set(ctx, serviceToken, tokenBytes, 0).Err(); err != nil {
		log.Println(err.Error())
		c.String(500, "Failed to save service token")
	}

	return c.Redirect(307, "/google")
}
