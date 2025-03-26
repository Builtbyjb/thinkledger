package redis

import (
	"log"
	"os"

	"github.com/redis/go-redis/v9"
)

func GetRedisClient() *redis.Client {
	redisUrl := os.Getenv("REDIS_URL")
	opt, err := redis.ParseURL(redisUrl)
	if err != nil {
		log.Println(err)
		return nil
	}

	client := redis.NewClient(opt)

	return client
}
