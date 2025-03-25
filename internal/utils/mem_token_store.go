package utils

import (
	"errors"

	"golang.org/x/oauth2"
)

type InMemoryTokenStore struct {
	tokens map[string]*oauth2.Token
}

func NewInMemoryTokenStore() *InMemoryTokenStore {
	return &InMemoryTokenStore{
		tokens: make(map[string]*oauth2.Token),
	}
}

func (s *InMemoryTokenStore) GetToken(userId string) (*oauth2.Token, error) {
	token, ok := s.tokens[userId]
	if !ok {
		return nil, errors.New("token not found")
	}
	return token, nil
}

func (s *InMemoryTokenStore) SaveToken(userId string, token *oauth2.Token) error {
	s.tokens[userId] = token
	return nil
}
