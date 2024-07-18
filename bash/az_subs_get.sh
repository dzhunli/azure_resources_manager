#!/bin/bash

SUBSCRIPTIONS=$(az account list --all --query '[].id' -o tsv)
TOTAL_SUBSCRIPTIONS=$(echo "$SUBSCRIPTIONS" | wc -w)
echo "Total subscriptions: $TOTAL_SUBSCRIPTIONS"
subscriptions_json=()
counter=1
for SUBSCRIPTION_ID in $SUBSCRIPTIONS; do
	echo "Processing subscription $counter of $TOTAL_SUBSCRIPTIONS: $SUBSCRIPTION_ID"
	owner=$(az resource list --subscription $SUBSCRIPTION_ID | jq -r '.[0].systemData.createdBy')
	if [ "$owner" = "null" ]; then
		enabled="false"
    	else
        	enabled="true"
    	fi
    	subscription_json=$(cat <<EOF
{
  "id": "$SUBSCRIPTION_ID",
  "enabled": $enabled,
  "owner": "$owner"
}
EOF
)
	subscriptions_json+=("$subscription_json")
	counter=$((counter + 1))
done
final_json=$(printf '%s\n' "${subscriptions_json[@]}" | jq -s '.')

echo "$final_json" > subscriptions.json
echo "JSON data has been saved to subscriptions.json"

