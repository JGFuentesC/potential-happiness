#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 1024

int main() {
    const char* filepath = "../../data/samples.csv";
    FILE* stream = fopen(filepath, "r");

    if (!stream) {
        printf("Error: Could not open file %s\n", filepath);
        return 1;
    }

    char line[MAX_LINE];
    int count = 0;
    double sum_val = 0, max_val = -1e9, min_val = 1e9;
    double sum_lat = 0, max_lat = -1e9, min_lat = 1e9;

    // Skip header
    fgets(line, MAX_LINE, stream);

    while (fgets(line, MAX_LINE, stream)) {
        char* tmp = strdup(line);
        
        // Tokenize csv manually for illustration
        char* token = strtok(tmp, ","); // id
        token = strtok(NULL, ",");      // value
        double val = atof(token);
        
        token = strtok(NULL, ",");      // latency
        double lat = atof(token);

        sum_val += val;
        if (val > max_val) max_val = val;
        if (val < min_val) min_val = val;

        sum_lat += lat;
        if (lat > max_lat) max_lat = lat;
        if (lat < min_lat) min_lat = lat;

        count++;
        free(tmp);
    }

    fclose(stream);

    printf("----------------------------------------\n");
    printf("C CSV Parsing Summary\n");
    printf("----------------------------------------\n");
    printf("Total Records: %d\n", count);
    printf("%-10s | %-10s | %-10s\n", "Metric", "Value", "Latency");
    printf("----------------------------------------\n");
    printf("%-10s | %-10.2f | %-10.3f\n", "Mean", sum_val / count, sum_lat / count);
    printf("%-10s | %-10.2f | %-10.3f\n", "Max", max_val, max_lat);
    printf("%-10s | %-10.2f | %-10.3f\n", "Min", min_val, min_lat);
    printf("----------------------------------------\n");

    return 0;
}
