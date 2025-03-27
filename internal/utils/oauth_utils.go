package utils

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/labstack/echo/v4"
	"golang.org/x/oauth2"
)

// Clear user authentication cookie
func ClearAuthIdCookie(c echo.Context) {
	c.SetCookie(&http.Cookie{
		Name:     "authId",
		Value:    "",
		HttpOnly: true,
		Path:     "/",
		Secure:   true,
		SameSite: http.SameSiteLaxMode,
		Expires:  time.Now().Add(5 * time.Minute),
	})
}

// Get user info from google
func GetUserInfo(accessToken string, oauthConfig *oauth2.Config) (*UserInfo, error) {
	client := oauthConfig.Client(context.Background(), &oauth2.Token{
		AccessToken: accessToken,
		TokenType:   "Bearer",
	})

	response, err := client.Get("https://www.googleapis.com/oauth2/v3/userinfo")
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
