#!/bin/bash

JSON_FILE="subscriptions.json"
BACKUP_FILE="subscriptions_backup.json"

if [ ! -f "$JSON_FILE" ]; then
   	 echo "JSON file not found: $JSON_FILE"
  	  exit 1
fi
cp "$JSON_FILE" "$BACKUP_FILE"
echo "Backup of JSON file created: $BACKUP_FILE"

CHECK_ALL=false
if [ "$1" == "--all" ]; then
	   CHECK_ALL=true
	echo "Validation will be performed for all subscriptions."
else
	echo "Validation will be performed for subscriptions with enabled=true."
fi

updated_subscriptions=()
jq -c '.[]' "$JSON_FILE" | while IFS= read -r subscription; do
	enabled=$(echo "$subscription" | jq -r '.enabled')
    	subscription_id=$(echo "$subscription" | jq -r '.id')

	if [ "$CHECK_ALL" == "true" ] || [ "$enabled" == "true" ]; then
        	output=$(az account show --subscription "$subscription_id" 2>&1)
        	if echo "$output" | grep -q "ERROR: (SubscriptionNotFound)"; then
            		echo "Subscription not found and will be removed from JSON: $subscription_id"
        	else
            		updated_subscriptions+=("$subscription")
        	fi
    	else
        	updated_subscriptions+=("$subscription")
    	fi
done

if [ ${#updated_subscriptions[@]} -eq 0 ]; then
	echo "No subscriptions remaining in JSON after validation."
	mv "$BACKUP_FILE" "$JSON_FILE"
else
	final_json=$(printf '%s\n' "${updated_subscriptions[@]}" | jq -s '.')
	echo "$final_json" > "$JSON_FILE"
	echo "Validation completed. Updated JSON saved to $JSON_FILE"
fi

