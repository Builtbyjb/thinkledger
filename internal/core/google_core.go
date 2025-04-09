package core

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"server/internal/utils"
	"time"

	"github.com/redis/go-redis/v9"
	"golang.org/x/oauth2"
	"google.golang.org/api/drive/v3"
	"google.golang.org/api/option"
	"google.golang.org/api/sheets/v4"
)

func UpdateTransactionSheet(
	r *redis.Client,
	oauth *oauth2.Config,
	transactions []utils.PlaidTransaction,
	userID string,
) error {
	ctx := context.Background()

	// Create google client
	serviceToken := "serviceToken:" + userID
	tokenStr, err := r.Get(ctx, serviceToken).Result()
	if err != nil {
		log.Print(err.Error())
		return err
	}

	var token *oauth2.Token
	if err := json.Unmarshal([]byte(tokenStr), &token); err != nil {
		log.Println(err)
		return err
	}

	client := oauth.Client(ctx, token)
	// Create drive service
	d, err := drive.NewService(ctx, option.WithHTTPClient(client))
	if err != nil {
		// TODO: handle failed token refresh
		log.Println(err)
		return err
	}

	// Create sheets service
	s, err := sheets.NewService(ctx, option.WithHTTPClient(client))
	if err != nil {
		// TODO: handle failed token refresh
		log.Println(err)
		return err
	}

	fileMetaData := &drive.File{
		Name:     "Thinkledger",
		MimeType: "application/vnd.google-apps.folder",
	}

	file, err := d.Files.Create(fileMetaData).Do()
	if err != nil {
		log.Println(err)
		return err
	}

	fmt.Println(file.Id)
	sFileMetadata := &drive.File{
		Name:     "test_spreadsheet",
		MimeType: "application/vnd.google-apps.spreadsheet", // **MimeType for Google Sheets**
		Parents:  []string{file.Id},                         // Set the parent folder
	}

	sFile, err := d.Files.Create(sFileMetadata).Fields("id, name, webViewLink").Do()
	if err != nil {
		log.Println(err)
		return err
	}

	fmt.Printf("Spreadsheet ID: %s\n", sFile.Id)
	// Data to write (slice of slices, each inner slice is a row)
	valuesToWrite := [][]any{
		{"Timestamp", "User", "Action", "Value"}, // Example Header Row
		{time.Now().Format(time.RFC3339), "user1@example.com", "LOGIN", 100},
		{time.Now().Add(1 * time.Minute).Format(time.RFC3339), "user2@example.com", "UPDATE", 25.5},
		{time.Now().Add(2 * time.Minute).Format(time.RFC3339), "user1@example.com", "LOGOUT", nil}, // nil becomes an empty cell
	}

	// Prepare the ValueRange object
	valueRange := &sheets.ValueRange{
		MajorDimension: "ROWS", // Write data row by row
		Values:         valuesToWrite,
	}

	// Specify the sheet and range (e.g., "Sheet1").
	// Appending to just "Sheet1" will add rows after the last row with data on that sheet.
	// If Sheet1 doesn't exist, the API often creates it.
	writeRange := "Sheet1"

	// Call the Append API
	appendCall := s.Spreadsheets.Values.Append(sFile.Id, writeRange, valueRange)
	appendCall.ValueInputOption("USER_ENTERED") // How the input data should be interpreted (USER_ENTERED or RAW)
	appendCall.InsertDataOption("INSERT_ROWS")  // How to insert (INSERT_ROWS or OVERWRITE)
	appendResp, err := appendCall.Do()
	if err != nil {
		log.Println(err)
		return err
	}

	fmt.Println(appendResp)

	return nil
}
