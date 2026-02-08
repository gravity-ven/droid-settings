#!/bin/bash
# Query Central Supermemory - Works for all CLI agents

SUPERMEMORY_API="http://localhost:3456"

case "$1" in
  search)
    if [ -z "$2" ]; then
      echo "Usage: memory-query.sh search <query>"
      exit 1
    fi
    curl -s -X POST "$SUPERMEMORY_API/api/memory/search" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$2\", \"limit\": ${3:-10}}" | \
      jq -r '.memories[] | "\n[\(.created_at)]\n\(.content)\n---"'
    ;;

  save)
    if [ -z "$2" ]; then
      echo "Usage: memory-query.sh save <content> [tag]"
      exit 1
    fi
    curl -s -X POST "$SUPERMEMORY_API/api/memory/save" \
      -H "Content-Type: application/json" \
      -d "{\"content\": \"$2\", \"containerTag\": \"${3:-general}\"}" | \
      jq '.'
    ;;

  all)
    curl -s "$SUPERMEMORY_API/api/memory/all?limit=${2:-50}" | \
      jq -r '.memories[] | "[\(.created_at)] [\(.container_tag // "no-tag")] \(.content)"'
    ;;

  profile)
    curl -s "$SUPERMEMORY_API/api/profile" | jq '.'
    ;;

  health)
    curl -s "$SUPERMEMORY_API/health" | jq '.'
    ;;

  *)
    echo "Central Memory Query Tool"
    echo "========================="
    echo ""
    echo "Usage: memory-query.sh <command> [args]"
    echo ""
    echo "Commands:"
    echo "  search <query> [limit]    Search memories (default limit: 10)"
    echo "  save <content> [tag]      Save a memory"
    echo "  all [limit]               List all memories (default limit: 50)"
    echo "  profile                   Get user profile + recent context"
    echo "  health                    Check server health"
    echo ""
    echo "Examples:"
    echo "  memory-query.sh search 'python errors'"
    echo "  memory-query.sh save 'Always use async/await for API calls' coding-rules"
    echo "  memory-query.sh all 20"
    ;;
esac
