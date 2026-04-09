package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
)

func main() {
	filepath := "../../data/samples.csv"
	file, err := os.Open(filepath)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	// Read header
	_, err = reader.Read()
	if err != nil {
		log.Fatal(err)
	}

	records, err := reader.ReadAll()
	if err != nil {
		log.Fatal(err)
	}

	var sumVal, maxVal, minVal float64
	var sumLat, maxLat, minLat float64
	minVal = 1e9
	minLat = 1e9

	for _, record := range records {
		val, _ := strconv.ParseFloat(record[1], 64)
		lat, _ := strconv.ParseFloat(record[2], 64)

		sumVal += val
		if val > maxVal {
			maxVal = val
		}
		if val < minVal {
			minVal = val
		}

		sumLat += lat
		if lat > maxLat {
			maxLat = lat
		}
		if lat < minLat {
			minLat = lat
		}
	}

	count := float64(len(records))

	fmt.Println("----------------------------------------")
	fmt.Println("Go CSV Parsing Summary")
	fmt.Println("----------------------------------------")
	fmt.Printf("Total Records: %d\n", len(records))
	fmt.Printf("%-10s | %-10s | %-10s\n", "Metric", "Value", "Latency")
	fmt.Println("----------------------------------------")
	fmt.Printf("%-10s | %-10.2f | %-10.3f\n", "Mean", sumVal/count, sumLat/count)
	fmt.Printf("%-10s | %-10.2f | %-10.3f\n", "Max", maxVal, maxLat)
	fmt.Printf("%-10s | %-10.2f | %-10.3f\n", "Min", minVal, minLat)
	fmt.Println("----------------------------------------")
}
