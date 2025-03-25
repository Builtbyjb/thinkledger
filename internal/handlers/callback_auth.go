package handlers

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/labstack/echo/v4"
	"golang.org/x/oauth2"
)

type UserInfo struct {
	Email string `json:"email"`
	Name  string `json:"name"`
}

func (h *Handler) HandleCallbackAuth(c echo.Context) error {
	// Verify state to prevent CSRF
	cookie, err := c.Cookie("state")
	if err != nil || cookie.Value != c.QueryParam("state") {
		log.Println(err)
		return c.String(http.StatusBadRequest, "Invalid state parameter")
	}

	userId, err := c.Cookie("user_id")
	if err != nil {
		log.Println(err)
		return c.String(http.StatusBadRequest, "Invalid user_id cookie")
	}

	token, err := h.OAuthConfig.Exchange(context.Background(), c.QueryParam("code"))
	if err != nil {
		log.Println(err)
		return c.String(
			http.StatusInternalServerError,
			"Token exchange failed: "+err.Error(),
		)
	}

	if err := h.TokenStore.SaveToken(userId.Value, token); err != nil {
		log.Println(err)
		return c.String(
			http.StatusInternalServerError,
			"Failed to save token: "+err.Error(),
		)
	}

	// Set user cookie
	c.SetCookie(&http.Cookie{
		Name:     "user_id",
		Value:    userId.Value,
		HttpOnly: true,
		Path:     "/",
		Secure:   true,
		Expires:  time.Now().Add(24 * time.Hour),
	})

	return c.Redirect(http.StatusTemporaryRedirect, "/home")
}

func getUserInfo(accessToken string, oauthConfig *oauth2.Config) (*UserInfo, error) {
	client := oauthConfig.Client(context.Background(), &oauth2.Token{
		AccessToken: accessToken,
		TokenType:   "Bearer",
	})

	response, err := client.Get("https://www.googleapis.com/oauth2/v2/userinfo")
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()

	if response.StatusCode != 200 {
		return nil, fmt.Errorf("google API returned status: %d", response.StatusCode)
	}

	data, err := io.ReadAll(response.Body)
	if err != nil {
		return nil, err
	}

	var userInfo UserInfo
	if err := json.Unmarshal(data, &userInfo); err != nil {
		return nil, err
	}

	return &userInfo, nil
}
