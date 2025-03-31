package utils

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

// Clear user authentication cookie
func ClearSessionIDCookie(c echo.Context) {
	c.SetCookie(&http.Cookie{
		Name:     "session_id",
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

func VerifyGoogleToken(token *oauth2.Token, oauthConfig *oauth2.Config) (*oauth2.Token, error) {
	ctx := context.Background()
	var verifiedToken = token

	// Check if the token as expired and try refreshing if there is a refresh token
	if token.Expiry.Before(time.Now()) {

		if token.RefreshToken == "" {
			return nil, fmt.Errorf("token has expired and no refresh token is available")
		}

		// Try refreshing the token
		newToken, err := oauthConfig.TokenSource(ctx, token).Token()
		if err != nil {
			return nil, fmt.Errorf("Error getting new token: %s", err)
		}

		verifiedToken = newToken
	}

	// Check if access token is valid
	isValid := verifyGoogleAccessToken(verifiedToken.AccessToken)
	if !isValid {
		return nil, fmt.Errorf("access toke is not valid")
	}

	return verifiedToken, nil
}

func verifyGoogleAccessToken(accessToken string) bool {
	client := &http.Client{Timeout: 10 * time.Second}
	tokenInfoURL := "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=" + accessToken

	response, err := client.Get(tokenInfoURL)
	if err != nil {
		log.Println("Token response error")
		return false
	}
	defer response.Body.Close()

	// Response status code would be 200 if the token is valid
	if response.StatusCode != 200 {
		log.Println("Token response status code error")
		return false
	}

	return true
}
