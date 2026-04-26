#!/bin/bash

# A script to test the rate limiting defined in slowapi_sample.py

# Base URL for the service
BASE_URL="http://0.0.0.0:8000"

# A helper function to make requests and print the HTTP status code.
# Usage: make_request <endpoint> [user-id]
function make_request() {
    local endpoint=$1
    local user_id=$2
    local http_code

    printf "Calling %-12s (User: %-10s) -> " "$endpoint" "${user_id:-anonymous}"

    if [ -n "$user_id" ]; then
        http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "user-id: $user_id" "$BASE_URL$endpoint")
    else
        http_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    fi

    echo "Status: $http_code"
}

# A helper function to pause the script and wait for user input.
function pause() {
    echo
    read -p ">>> Press [Enter] to continue, or [Ctrl+C] to exit."
    echo
    echo
    echo
    echo
    echo
    echo
    echo "================== START =================="
}

# Wait for the server to be ready
echo "Waiting 2 seconds for server to start..."
sleep 2

echo
echo "The script will now run through a series of tests."
echo "It will pause between each major test section."
pause

# =====================================================
# 1. Test Single Endpoint Rate Limit (/single)
#    Limit: 2 requests per 60 seconds
# =====================================================
echo
echo "====================================================="
echo "1. Testing Single Endpoint Rate Limit (/single)"
echo "   Limit is 2 per 60s. Making 3 requests."
echo "   -> Expecting: 200, 200, 429"
echo "====================================================="
for i in $(seq 3); do
    make_request "/single"
    sleep 0.5 # Short sleep to stay within the time limit window
done

pause

# Wait for limits to reset
echo
echo "--> Waiting 60 seconds for limits to reset..."
sleep 60

# =====================================================
# 2. Test Per-User Rate Limit (/per-user)
#    Limit: 5 requests per 60 seconds for each user-id
# =====================================================
echo
echo "====================================================="
echo "2. Testing Per-User Rate Limit (/per-user)"
echo "   Limit is 5 per 60s per user-id."
echo "====================================================="
echo
echo "--- Part A: Test 'user1'. Making 6 requests."
echo "    -> Expecting: 200, 200, 200, 200, 200, 429"
echo "---"
for i in $(seq 6); do
    make_request "/per-user" "user1"
    sleep 0.5
done
echo
echo "--- Part B: Test 'user2'. Making 1 request."
echo "    -> Expecting: 200 (separate from user1)"
echo "---"
make_request "/per-user" "user2"
echo
echo "--- Part C: Test anonymous user. Making 6 requests."
echo "    -> Expecting: 200, 200, 200, 200, 200, 429"
echo "---"
for i in $(seq 6); do
    make_request "/per-user"
    sleep 0.5
done

pause

# Wait for limits to reset
echo
echo "--> Waiting 60 seconds for limits to reset..."
sleep 60

# =====================================================
# 3. Test Global Rate Limit (All endpoints)
#    Limit: 10 requests per 60 seconds for the service
# =====================================================
echo
echo "====================================================="
echo "3. Testing Global Rate Limit"
echo "   Limit is 10 per 60s across all APIs. Making 11 requests."
echo "   The 11th request should be blocked by the global limit."
echo "====================================================="
echo "--- Making 2 requests to /single (Limit 2/min)"
make_request "/single"; sleep 0.2
make_request "/single"; sleep 0.2
echo "--> Used 2/10 of global limit. OK."
echo
echo "--- Making 5 requests to /per-user (user: 'global-test-2')"
for i in $(seq 5); do
    make_request "/per-user" "global-test-2"; sleep 0.2
done
echo "--> Used 7/10 of global limit. OK."
echo
echo "--- Making 3 requests to /per-user (user: 'global-test')"
for i in $(seq 3); do
    make_request "/per-user" "global-test"; sleep 0.2
done
echo "--> Used 10/10 of global limit. OK."
echo
echo "--- Making 1 final request to /per-user (user: 'global-test')"
echo "    This is the 11th request in total."
echo "    -> Expecting: 429 (blocked by GLOBAL limit)"
echo "---"
make_request "/per-user" "global-test"
make_request "/per-user" "global-test"
make_request "/per-user" "global-test"

pause

echo
echo "====================================================="
echo "All tests finished."
echo "====================================================="
