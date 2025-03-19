package handlers

import (
	"fmt"
	"log"

	"github.com/gofiber/fiber/v2"
)

type ChatEvent struct {
	Type      string `json:"type"`
	EventTime string `json:"eventTime"`
	Space     struct {
		Name        string `json:"name"`
		Type        string `json:"type"`
		DisplayName string `json:"displayName"`
	} `json:"space"`
	Message struct {
		Name       string `json:"name"`
		CreateTime string `json:"createTime"`
		Sender     struct {
			Name        string `json:"name"`
			DisplayName string `json:"displayName"`
			Email       string `json:"email"` // May be empty for Chat apps
		} `json:"sender"`
		Text   string `json:"text"`
		Thread struct {
			Name string `json:"name"`
		} `json:"thread"`
	} `json:"message,omitempty"` // message is present for MESSAGE events
}

func (h *Handler) HandleChat(c *fiber.Ctx) error {

	var chatEvent ChatEvent
	if err := c.BodyParser((&chatEvent)); err != nil {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	log.Printf("Chat event received: %+v", chatEvent)

	// TODO: Make more reboust

	if chatEvent.Type == "MESSAGE" && chatEvent.Message.Text != "" {
		receivedMessage := chatEvent.Message.Text
		senderName := chatEvent.Message.Sender.DisplayName
		// spaceName := chatEvent.Space.Name
		// threadName := chatEvent.Message.Thread.Name

		responseMessage := fmt.Sprintf("Hello %s, you said: %s", senderName, receivedMessage)

		// err := sendMessage(spaceName, threadName, responseMessage)
		// if err != nil {
		// 	log.Printf("Error sending message: %v", err)
		// 	return c.SendStatus(fiber.StatusInternalServerError) // Return 500 for server error

		// }
		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"text": responseMessage,
		})
	} else {
		log.Println("Ignoring non-MESSAGE event or empty message")

		return c.Status(fiber.StatusOK).JSON(fiber.Map{
			"text": "I am currently ignoring non-MESSAGE events or empty messages",
		})
	}

}

// func sendMessage(spaceName, threadName, messageText string) error {

// 	// Get access token
// 	token, err := getAccessToken()
// 	if err != nil {
// 		return fmt.Errorf("authentication error: %v", err)
// 	}

// 	ctx := context.Background()

// 	chatService, err := chat.NewService(ctx, option.WithTokenSource(
// 		// oauth2.StaticTokenSource(&oauth2.Token{AccessToken: token}), // For testing certain tokens
// 		token,
// 	))

// 	if err != nil {
// 		return fmt.Errorf("failed to create chat service: %v", err)
// 	}

// 	message := &chat.Message{
// 		Text: messageText,
// 	}

// 	// Use thread key to ensure replies are in the same thread.
// 	_, err = chatService.Spaces.Messages.Create(spaceName, message).ThreadKey(threadName).Do()
// 	if err != nil {
// 		return fmt.Errorf("failed to send message: %v", err)
// 	}

// 	log.Println("Message sent successfully to Google Chat")
// 	return nil
// }

// func getAccessToken() (oauth2.TokenSource, error) {

// 	privateKey := strings.ReplaceAll(os.Getenv("GOOGLE_PRIVATE_KEY"), `\n`, "\n")

// 	// Construct JSON credentials from environment variables
// 	credentials := map[string]interface{}{
// 		"type":                        os.Getenv("GOOGLE_TYPE"),
// 		"project_id":                  os.Getenv("GOOGLE_PROJECT_ID"),
// 		"private_key_id":              os.Getenv("GOOGLE_PRIVATE_KEY_ID"),
// 		"private_key":                 privateKey,
// 		"client_email":                os.Getenv("GOOGLE_CLIENT_EMAIL"),
// 		"client_id":                   os.Getenv("GOOGLE_CLIENT_ID"),
// 		"auth_uri":                    os.Getenv("GOOGLE_AUTH_URI"),
// 		"token_uri":                   os.Getenv("GOOGLE_TOKEN_URI"),
// 		"auth_provider_x509_cert_url": os.Getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
// 		"client_x509_cert_url":        os.Getenv("GOOGLE_CLIENT_X509_CERT_URL"),
// 		"universe_domain":             os.Getenv("GOOGLE_UNIVERSE_DOMAIN"),
// 	}

// 	jsonBytes, err := json.Marshal(credentials)
// 	if err != nil {
// 		return nil, fmt.Errorf("failed to marshal JSON credentials: %v", err)
// 	}

// 	// Configure JWT claims
// 	config, err := google.JWTConfigFromJSON(
// 		jsonBytes,
// 		os.Getenv("GOOGLE_SERVICE_SCOPE"), // scope
// 	)
// 	if err != nil {
// 		return nil, fmt.Errorf("unable to create JWT config: %v", err)
// 	}

// 	ctx := context.Background()

// 	// Get token source
// 	tokenSource := config.TokenSource(ctx)

// 	// token, err := tokenSource.Token() // Getting the actual access token
// 	// if err != nil {
// 	// 	return "", fmt.Errorf("unable to get token: %v", err)
// 	// }

// 	// return token.AccessToken, nil

// 	return tokenSource, nil
// }

// Sanitize transaction prompt
// func generatePrompt(transaction string) (string, error) {

// 	if len(transaction) == 0 {
// 		return "", errors.New("Transaction cannot be empty")
// 	}

// 	prompt := fmt.Sprintf(`Create a journal entry for this transaction "%s"`, transaction)

// 	return prompt, nil
// }

// // Add journal entry accounts to the database
// func addAccounts(
// 	db *gorm.DB,
// 	journalId uuid.UUID,
// 	accounts []utils.AccountDetail,
// 	t string, // Debit or Credit
// ) error {

// 	var r *gorm.DB

// 	for i := range len(accounts) {

// 		var account database.Account

// 		// Check if an account with this account name exist
// 		accountResult := db.Where("account_name", accounts[i].AccountName).First(&account)

// 		if accountResult.Error != nil {
// 			// if there is an error, The account does not exist. Create a new account
// 			account = database.Account{
// 				Id:            uuid.New(),
// 				AccountName:   accounts[i].AccountName,
// 				AccountRef:    generateAccountRef(db),
// 				AccountType:   accounts[i].AccountType,
// 				NormalBalance: accounts[i].NormalBalance,
// 			}

// 			r = db.Create(&account)
// 			if r.Error != nil {
// 				return fmt.Errorf("could not add account to database: %w", r.Error)
// 			}
// 		}

// 		amount, err := strconv.Atoi(accounts[i].Amount)
// 		if err != nil {
// 			return fmt.Errorf("unable to convert credit amount string to int: %w", err)
// 		}

// 		if t == "credit" {
// 			credit := database.Credit{
// 				JournalId:   journalId,
// 				AccountId:   account.Id,
// 				AccountName: accounts[i].AccountName,
// 				AccountRef:  account.AccountRef,
// 				Amount:      amount,
// 			}

// 			r = db.Create(&credit)
// 			if r.Error != nil {
// 				return fmt.Errorf("count not add credit account to database: %w", r.Error)
// 			}
// 		} else {
// 			debit := database.Debit{
// 				JournalId:   journalId,
// 				AccountId:   account.Id,
// 				AccountRef:  account.AccountRef,
// 				AccountName: accounts[i].AccountName,
// 				Amount:      amount,
// 			}

// 			r = db.Create(&debit)
// 			if r.Error != nil {
// 				return fmt.Errorf("count not add credit account to database: %w", r.Error)
// 			}
// 		}
// 	}
// 	return nil
// }

// // Generate Account references
// func generateAccountRef(db *gorm.DB) string {
// 	const base int = 100

// 	var a []database.Account
// 	result := db.Find(&a)

// 	if result.Error != nil {
// 		log.Fatalf("database error: %v", result.Error)
// 	}

// 	length := int(result.RowsAffected) + base

// 	accountRef := fmt.Sprintf("J%v", length)

// 	return accountRef
// }
