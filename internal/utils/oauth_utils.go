package utils

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/redis/go-redis/v9"
	"golang.org/x/oauth2"
)

// Save user sign in token
func SaveUserSignInToken(
	r *redis.Client,
	token *oauth2.Token,
	userID string,
) error {
	ctx := context.Background()
	tokenBytes, err := json.Marshal(token)
	if err != nil {
		return err
	}
	userSignInToken := "signInToken:" + userID
	if err := r.Set(ctx, userSignInToken, tokenBytes, 0).Err(); err != nil {
		return err
	}
	return nil
}

// Get user sign in token
func GetUserSignInToken(r *redis.Client, userID string) (*oauth2.Token, error) {
	ctx := context.Background()
	userSignInToken := "signInToken:" + userID
	tokenStr, err := r.Get(ctx, userSignInToken).Result()
	if err != nil {
		return nil, errors.New("Failed to get user sign in token")
	}
	var token *oauth2.Token
	if err := json.Unmarshal([]byte(tokenStr), &token); err != nil {
		return nil, err
	}
	return token, nil
}

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

func RefreshGoogleToken(
	token *oauth2.Token,
	oauthConfig *oauth2.Config,
) (*oauth2.Token, error) {
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
	return verifiedToken, nil
}

func VerifyGoogleAccessToken(accessToken string) (bool, error) {
	client := &http.Client{Timeout: 10 * time.Second}
	tokenInfoURL := "https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=" + accessToken

	response, err := client.Get(tokenInfoURL)
	if err != nil {
		return false, errors.New("Access token response error")
	}
	defer response.Body.Close()

	// Response status code would be 200 if the token is valid
	if response.StatusCode != 200 {
		log.Println("Token response status code error")
		return false, errors.New("Invalid access token")
	}
	return true, nil
}
