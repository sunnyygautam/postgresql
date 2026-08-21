#!/bin/bash

# ==========================================
# CONFIGURATION
# ==========================================
# Thresholds
MAX_CPU=80         # Alert if overall CPU usage > 80%
MAX_MEM=85         # Alert if overall RAM usage > 85%
MAX_DISK=90        # Alert if Disk usage > 90%
PROC_MEM_LIMIT=5.0 # Alert if a single process uses > 5.0% RAM (Decimal ok)

# Monitoring Targets
PROCESSES=("nginx" "mysql" "node")                  # Critical process names to check
PORTS=(80 443 3306)                                 # Critical local ports to check
URLS=("http://localhost" "https://google.com")      # Critical URLs to check

# Logging
LOG_FILE="/var/log/app_monitor.log"                 # Change path if you lack root permissions
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# ==========================================
# HELPER FUNCTIONS
# ==========================================
log_alert() {
    local message="[ALERT] [$TIMESTAMP] $1"
    echo -e "\e[31m$message\e[0m" # Print in red text
    echo "$message" >> "$LOG_FILE" 2>/dev/null || echo "$message" >> "./app_monitor.log"
}

log_ok() {
    echo -e "\e[32m[OK] [$TIMESTAMP] $1\e[0m" # Print in green text
}

# ==========================================
# MONITORS
# ==========================================

echo "=== Starting System & Application Monitor ==="

# 1. System-Wide CPU Usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
CPU_INT=${CPU_USAGE%.*} # Convert to integer for Bash comparison
if [ "$CPU_INT" -gt "$MAX_CPU" ]; then
    log_alert "High System CPU Usage: ${CPU_USAGE}% (Threshold: ${MAX_CPU}%)"
else
    log_ok "System CPU Usage: ${CPU_USAGE}%"
fi

# 2. System-Wide Memory Usage
MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100}')
MEM_INT=${MEM_USAGE%.*}
if [ "$MEM_INT" -gt "$MAX_MEM" ]; then
    log_alert "High System Memory Usage: ${MEM_USAGE}% (Threshold: ${MAX_MEM}%)"
else
    log_ok "System Memory Usage: ${MEM_USAGE}%"
fi

# 3. Disk Usage Check (Root Partition)
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt "$MAX_DISK" ]; then
    log_alert "High Disk Usage on /: ${DISK_USAGE}% (Threshold: ${MAX_DISK}%)"
else
    log_ok "Disk Usage on /: ${DISK_USAGE}%"
fi

# 4. Top Process Memory Hog Check (Fixing your original logic)
ps aux --sort=-%mem | awk -v limit="$PROC_MEM_LIMIT" '
    NR>1 && $4 > limit {
        print "HOG:" $11 " (PID " $2 ") is using " $4 "% memory"
    }
' | while read -r line; do
    log_alert "Memory Hog Found -> ${line#HOG:}"
done

# 5. Critical Process Status Check
for proc in "${PROCESSES[@]}"; do
    if ! pgrep -x "$proc" > /dev/null; then
        log_alert "Process '$proc' is NOT running!"
    else
        log_ok "Process '$proc' is running."
    fi
done

# 6. Local Port Check
for port in "${PORTS[@]}"; do
    if ! ss -tuln | grep -q ":$port "; then
        log_alert "Port $port is NOT listening!"
    else
        log_ok "Port $port is open and listening."
    fi
done

# 7. Website / URL HTTP Status Check
for url in "${URLS[@]}"; do
    # Fetch HTTP status code (timeout after 5 seconds)
    HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}" --connect-timeout 5 "$url")
    if [ "$HTTP_STATUS" -ne 200 ] && [ "$HTTP_STATUS" -ne 301 ] && [ "$HTTP_STATUS" -ne 302 ]; then
        log_alert "URL '$url' returned bad status code: $HTTP_STATUS"
    else
        log_ok "URL '$url' is reachable (Status: $HTTP_STATUS)"
    fi
done

echo "=== Monitor Run Complete ==="
