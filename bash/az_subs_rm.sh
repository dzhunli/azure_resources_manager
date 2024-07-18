#!/bin/bash
admin_id=
JSON_FILE="subscriptions.json"

if [ ! -f "$JSON_FILE" ]; then
	echo "JSON file not found: $JSON_FILE"
	exit 1
fi

if [ -f "deletion.log" ]; then
	echo  "" > deletion.log
fi

jq -c '.[]' "$JSON_FILE" | while read -r subscription; do
	enabled=$(echo "$subscription" | jq -r '.enabled')
	subscription_id=$(echo "$subscription" | jq -r '.id')
    
	if [ "$enabled" == "false" ]; then
		echo "-----------------------------------------"    
        	echo "Processing subscription: $subscription_id"
		echo "Processing subscription: $subscription_id" >> deletion.log
		resources=$(az resource list --subscription "$subscription_id" --query '[].id' -o tsv)
        	if [ -z "$resources" ]; then
            		echo "No resources found for subscription: $subscription_id. Skipping."
            		echo "No resources found for subscription: $subscription_id. Skipping." >> deletion.log
        		echo "Deleting subscription: $subscription_id"

			TOKEN=$(az account get-access-token --query accessToken -o tsv)
                	az role assignment create --role "Owner" --assignee "$admin_id" --subscription "$subscription_id" --scope "/subscriptions/${subscription_id}" 2>&1 > /dev/null
			az account set --subscription $subscription_id
			sleep 5
			curl -X POST https://management.azure.com/subscriptions/$subscription_id/providers/Microsoft.Subscription/cancel?api-version=2021-10-01 \
				-H "Authorization: Bearer $TOKEN" \
				-H "Content-Type: application/json" \
				-d '{}' \
				-H "Content-Length: 2"
			echo ""
        		az role assignment delete --role "Owner" --assignee "$admin_id" --scope "/subscriptions/$subscription_id"
			echo "-----------------------------------------" 
	    		continue
        	fi
		az role assignment create --role "Owner" --assignee "$admin_id" --subscription "$subscription_id" --scope "/subscriptions/${subscription_id}" 2>&1 > /dev/null
        	az account set --subscription $subscription_id
		sleep 6 
		while IFS= read -r resource_id; do
    			echo "Deleting resource: $resource_id"
    			echo "Deleting resource: $resource_id" >> deletion.log
    			az resource delete --ids "$resource_id"
		done <<< "$resources"
		az role assignment delete --role "Owner" --assignee "$admin_id" --scope "/subscriptions/$subscription_id"
		echo "-----------------------------------------"    
	else
        	echo "Skipping subscription (enabled=true): $subscription_id" >> deletion.log
#		echo "Skipping subscription (enabled=false): $subscription_id"
	fi
done

echo "Processing completed."

