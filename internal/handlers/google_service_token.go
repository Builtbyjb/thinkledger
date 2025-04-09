package handlers

import (
	"encoding/json"
	"log"
	"net/http"
	"server/internal/utils"
	"time"

	"github.com/labstack/echo/v4"
	"golang.org/x/oauth2"
)

func (h *Handler) GoogleServiceToken(c echo.Context) error {
	ctx := c.Request().Context()

	var scopes []string
	var googleSheet string = "false"
	var googleDrive string = "false"

	// TODO: prevent getting of new token if the previous tokens are still valid
	if c.QueryParam("googlesheet") == "on" {
		googleSheet = "true"
		scopes = append(scopes, "https://www.googleapis.com/auth/spreadsheets")
	}

	if c.QueryParam("googledrive") == "on" {
		googleDrive = "true"
		scopes = append(scopes, "https://www.googleapis.com/auth/drive.file")
	}

	cookie, err := c.Request().Cookie("session_id")
	if err != nil || cookie.Value == "" {
		log.Println(err)
		return c.Redirect(307, "/")
	}

	sessionID := cookie.Value

	userID, err := h.RedisClient.Get(ctx, sessionID).Result()
	if err != nil {
		log.Println(err.Error())
		return c.String(500, "Internal server error")
	}

	activeScopes := utils.ActiveScopes{
		GoogleSheet: googleSheet,
		GoogleDrive: googleDrive,
	}

	activeScopesBytes, err := json.Marshal(activeScopes)
	if err != nil {
		log.Println(err)
		return c.JSON(500, map[string]string{
			"error": "Internal server error",
		})
	}

	userScopes := "scopes:" + userID
	if err := h.RedisClient.Set(ctx, userScopes, activeScopesBytes, 0).Err(); err != nil {
		log.Println(err.Error())
		return c.JSON(500, map[string]string{
			"error": "Internal server error",
		})
	}

	for _, s := range scopes {
		h.ServiceAuthConfig.Scopes = append(h.ServiceAuthConfig.Scopes, s)
	}

	if len(scopes) > 0 {
		config := &oauth2.Config{
			ClientID:     h.ServiceAuthConfig.ClientID,
			ClientSecret: h.ServiceAuthConfig.ClientSecret,
			RedirectURL:  h.ServiceAuthConfig.RedirectURL,
			Scopes:       h.ServiceAuthConfig.Scopes,
			Endpoint:     h.ServiceAuthConfig.Endpoint,
		}

		serviceState, err := utils.GenerateRandomstring()
		if err != nil {
			log.Println(err)
			c.String(500, "Internal server error")
		}

		c.SetCookie(&http.Cookie{
			Name:     "service_state",
			Value:    serviceState,
			HttpOnly: true,
			Path:     "/",
			Secure:   true,
			Expires:  time.Now().Add(5 * time.Minute),
		})

		// Include the ApprovalForce option to request incremental auth
		// Include the AccessOffline option to request a refresh token
		url := config.AuthCodeURL(serviceState)
		return c.Redirect(307, url)
	} else {
		return c.JSON(400, map[string]string{
			"error": "Must connect at least one google service",
		})
	}
}
