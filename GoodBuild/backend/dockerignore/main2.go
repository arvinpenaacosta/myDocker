package main

import (
    "database/sql"
    "fmt"
    "log"
    "net/http"
    "os"
    "html/template"

    "github.com/gin-gonic/gin"
    _ "github.com/denisenkom/go-mssqldb" // Import mssql driver
    "github.com/joho/godotenv"
)

var db *sql.DB
var templates *template.Template

// Load environment variables
func loadEnv() {
    err := godotenv.Load()
    if err != nil {
        log.Fatalf("Error loading .env file")
    }
}

// Connect to the database
func getDbConnection() (*sql.DB, error) {
    dbUser := os.Getenv("DB_USER")
    dbPassword := os.Getenv("DB_PASSWORD")
    dbName := os.Getenv("DB_NAME")
    dbHost := os.Getenv("DB_HOST")

    connectionString := fmt.Sprintf("sqlserver://%s:%s@%s?database=%s", dbUser, dbPassword, dbHost, dbName)
    return sql.Open("sqlserver", connectionString)
}

func main() {
    loadEnv()

    // Connect to the database
    var err error
    db, err = getDbConnection()
    if err != nil {
        log.Fatal("Failed to connect to database:", err)
    }
    defer db.Close()

    // Initialize Gin router
    router := gin.Default()

    // Load HTML templates using html/template package
    tmpl := template.Must(template.ParseGlob("templates/*.html"))

    // Set the HTML template engine to use the loaded templates
    router.SetHTMLTemplate(tmpl)

    // Serve static files
    router.Static("/statics", "./statics")

    // Define routes
    router.GET("/", func(c *gin.Context) {
        distinctWord := os.Getenv("DistinctWord")
        kbPatch := os.Getenv("KBPatch")

        rows, err := db.Query("SELECT field1, field2 FROM entries")
        if err != nil {
            c.String(http.StatusInternalServerError, err.Error())
            return
        }
        defer rows.Close()

        var entries []struct {
            Field1 string
            Field2 string
        }

        for rows.Next() {
            var field1, field2 string
            if err := rows.Scan(&field1, &field2); err != nil {
                c.String(http.StatusInternalServerError, err.Error())
                return
            }
            entries = append(entries, struct {
                Field1 string
                Field2 string
            }{field1, field2})
        }

        c.HTML(http.StatusOK, "indexgo.html", gin.H{
            "DistinctWord": distinctWord,
            "KBPatch":      kbPatch,
            "Entries":      entries,
        })
    })

    router.POST("/api/submit", func(c *gin.Context) {
        field1 := c.PostForm("field1")
        field2 := c.PostForm("field2")

        _, err := db.Exec("INSERT INTO entries (field1, field2) VALUES (@p1, @p2)", field1, field2)
        if err != nil {
            c.String(http.StatusInternalServerError, err.Error())
            return
        }

        c.Redirect(http.StatusFound, "/")
    })

    certDir := "certs"
    sslKeyfile := fmt.Sprintf("%s/server_unencrypted.key", certDir)
    sslCertfile := fmt.Sprintf("%s/server.crt", certDir)

    // Start HTTPS server with SSL
    log.Println("Starting server on https://localhost:8857")
    err = router.RunTLS(":8857", sslCertfile, sslKeyfile)
    if err != nil {
        log.Fatal("Failed to start HTTPS server:", err)
    }
}
