# Advanced Shell Scripting Cheat Sheet

## Script Foundations
```bash
#!/bin/bash
set -e        # Exit on error
set -u        # Error on undefined variables
set -o pipefail # Exit on pipe failures
set -x        # Print commands before execution (debug)

# Source external configurations
source "./config.sh"
. "./config.sh"    # Alternative syntax
```

## Essential Variables and Environment
```bash
# Special Variables
$0          # Script name
$1, $2      # Positional arguments
$#          # Number of arguments
$@          # All arguments as separate strings
$*          # All arguments as single string
$?          # Last command exit status
$$          # Current process ID
$!          # Last background process ID
${PIPESTATUS[0]} # Exit status of piped commands

# Variable Operations
${var:-default}     # Use default if var undefined
${var:=default}     # Set default if var undefined
${var:?error_msg}   # Display error if var undefined
${var:+value}       # Use alternate if var defined
${var:offset:length}# Substring extraction
${#var}            # String length
${var#pattern}     # Remove shortest match from start
${var##pattern}    # Remove longest match from start
${var%pattern}     # Remove shortest match from end
${var%%pattern}    # Remove longest match from end
```

## Function Definitions and Usage
```bash
# Function Definition
function_name() {
    local local_var="local scope"    # Local variable
    echo "$1"                        # First argument
    return 0                         # Return status
}

# Alternative Definition
function function_name {
    # Function body
}

# Function Usage
result=$(function_name "arg1")
function_name "arg1" || exit 1

# Exit Trap
cleanup() {
    # Cleanup operations
}
trap cleanup EXIT
```

## Error Handling and Logging
```bash
# Error Function
error() {
    local msg="$1"
    local code="${2:-1}"
    local line="${BASH_LINENO[0]}"
    echo "Error on line $line: $msg" >&2
    exit "$code"
}

# Logging Function
log() {
    local level="$1"
    shift
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $*" >&2
}

# Usage
log INFO "Starting deployment"
[[ -f config.yml ]] || error "Config file missing" 2

# Redirect stdout and stderr
exec 1> >(tee -a "${LOG_FILE}")
exec 2> >(tee -a "${LOG_FILE}" >&2)
```

## Process Management
```bash
# Background Processes
long_task & 
PID=$!
wait $PID

# Timeout Command
timeout 5s command || error "Command timed out"

# Process Groups
set -m  # Enable job control
(
    command1 &
    command2 &
    wait
)

# Lock File
LOCK_FILE="/var/run/script.lock"
(
    flock -n 200 || exit 1
    # Critical section
) 200>"$LOCK_FILE"
```

## File Operations and Checks
```bash
# File Tests
[[ -f file ]]  # Regular file exists
[[ -d dir ]]   # Directory exists
[[ -r file ]]  # File is readable
[[ -w file ]]  # File is writable
[[ -x file ]]  # File is executable
[[ -s file ]]  # File is not empty
[[ file1 -nt file2 ]]  # file1 newer than file2

# File Operations
mkdir -p "dir/subdir"
rm -rf "dir"
find . -type f -name "*.log" -mtime +7 -delete
rsync -avz --progress src/ dest/

# Temporary Files
temp_file=$(mktemp)
temp_dir=$(mktemp -d)
trap 'rm -rf "$temp_file" "$temp_dir"' EXIT
```

## Network Operations
```bash
# Wait for Service
wait_for_port() {
    local host="$1"
    local port="$2"
    local timeout="${3:-30}"
    
    until nc -z "$host" "$port" || [ $timeout -le 0 ]; do
        sleep 1
        timeout=$((timeout-1))
    done
    
    [[ $timeout -gt 0 ]] || error "Service startup timed out"
}

# HTTP Requests
curl -sSL -X POST \
     -H "Content-Type: application/json" \
     -d '{"key":"value"}' \
     https://api.example.com

# Check URL Availability
check_url() {
    curl -sSf "$1" >/dev/null 2>&1
}
```

## String and Array Operations
```bash
# Array Operations
declare -a array=("item1" "item2" "item3")
array+=("item4")
echo "${array[@]}"          # All elements
echo "${#array[@]}"         # Array length
echo "${array[@]:1:2}"      # Slice

# String Operations
string="Hello,World"
echo "${string/,/-}"        # Replace first occurrence
echo "${string//,/-}"       # Replace all occurrences
echo "${string^}"           # Capitalize first char
echo "${string^^}"          # Convert to uppercase
echo "${string,,}"          # Convert to lowercase

# Split String
IFS=',' read -ra ADDR <<< "$string"
for i in "${ADDR[@]}"; do
    echo "$i"
done
```

## Deployment Helpers
```bash
# Version Management
get_version() {
    git describe --tags --always || echo "unknown"
}

# Config Management
load_config() {
    local env="$1"
    local config_file="config.$env.yml"
    [[ -f "$config_file" ]] || error "Missing config for $env"
    parse_yaml "$config_file"
}

# Health Check
health_check() {
    local url="$1"
    local attempts=5
    while [[ $attempts -gt 0 ]]; do
        if check_url "$url"; then
            return 0
        fi
        attempts=$((attempts-1))
        sleep 2
    done
    return 1
}

# Rolling Deployment
rolling_deploy() {
    local servers=($@)
    for server in "${servers[@]}"; do
        log INFO "Deploying to $server"
        ssh "$server" "./deploy.sh" || error "Deploy failed on $server"
        health_check "http://$server/health" || error "Health check failed"
    done
}
```

## Best Practices
1. Always use double quotes around variables
2. Use meaningful variable and function names
3. Include proper error handling and logging
4. Add cleanup traps for temporary resources
5. Use local variables in functions
6. Include proper parameter validation
7. Add helpful comments for complex operations
8. Use shellcheck for static analysis
9. Implement proper timeout handling
10. Include usage documentation

## Common Gotchas
1. Remember to handle spaces in filenames
2. Be careful with wildcard expansion
3. Check command existence before usage
4. Handle SSH agent properly in automated scripts
5. Be aware of different shell versions and compatibility
6. Remember to set proper file permissions
7. Handle script interruption properly
8. Be careful with eval and command injection
9. Remember to validate all inputs
10. Be aware of maximum command line length limitations
