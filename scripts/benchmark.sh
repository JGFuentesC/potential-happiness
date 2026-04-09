#!/bin/bash

# Rigorous Benchmark Suite for CSV Parsing
# Author: Antigravity for Dr. Fuentes
# OS: macOS (Darwin)

SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( dirname "$SCRIPTS_DIR" )"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Industrial Benchmark Suite ===${NC}"
echo "Date: $(date)"
echo "-------------------------------------"

# 1. Compilation
echo -e "${YELLOW}[System] Starting compilation phase...${NC}"
echo -n "  > Compiling C... "
(cd "$ROOT_DIR/src/c" && make clean && make) > /dev/null 2>&1 && echo -e "${GREEN}DONE${NC}" || echo -e "${RED}FAILED${NC}"

echo -n "  > Compiling Go... "
(cd "$ROOT_DIR/src/go" && go build -o parser main.go) > /dev/null 2>&1 && echo -e "${GREEN}DONE${NC}" || echo -e "${RED}FAILED${NC}"

echo -n "  > Python Environment... "
[ -d "$ROOT_DIR/src/python/.venv" ] && echo -e "${GREEN}READY${NC}" || (cd "$ROOT_DIR/src/python" && uv sync > /dev/null 2>&1 && echo -e "${GREEN}INITIALIZED${NC}")

# 2. Execution (WITH CD to respect relative paths in codes)
run_benchmark() {
    local dir=$1
    local bin=$2
    local label=$3
    
    echo -e "\n${BLUE}--- [AUDIT] ${label} ---${NC}"
    
    # Run from the source directory to maintain path consistency
    cd "$dir"
    /usr/bin/time -l $bin 2> /tmp/bench_stats
    
    # Extract metrics
    local real_time=$(grep "real" /tmp/bench_stats | awk '{print $1}')
    local max_rss=$(grep "maximum resident set size" /tmp/bench_stats | awk '{print $1}')
    local rss_mib=$(echo "scale=2; $max_rss / 1048576" | bc)
    
    echo -e "\n${YELLOW}Performance Metrics [${label}]:${NC}"
    echo "  - Time: ${real_time}s | RAM: ${rss_mib} MiB"
}

# Run implementations
run_benchmark "$ROOT_DIR/src/python" "uv run main.py" "Python (uv)"
run_benchmark "$ROOT_DIR/src/c" "./csv_parser" "C (Native)"
run_benchmark "$ROOT_DIR/src/go" "./parser" "Go (Binary)"

echo -e "\n${BLUE}-------------------------------------${NC}"
echo -e "${BLUE}Benchmark Audit Completed.${NC}"
rm -f /tmp/bench_stats
