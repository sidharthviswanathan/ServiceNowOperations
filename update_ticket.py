import os
import json
import requests
from requests.auth import HTTPBasicAuth


INSTANCE = os.environ.get('SERVICENOW_INSTANCE_NAME')
BASE_URL = os.environ.get('SERVICENOW_INSTANCE')
USERNAME = os.environ.get('SERVICENOW_USERNAME')
PASSWORD = os.environ.get('SERVICENOW_PASSWORD')



def test_connection():
    url = f"{BASE_URL}/api/now/table/incident?sysparm_limit=1"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            print("✅ Connection to ServiceNow instance successful!")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed. Check your username/password.")
            return False
        else:
            print(f"❌ Connection failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}. Check your instance URL.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection timed out.")
        return False


def create_incident(
        short_description,
        description="",
        urgency="2",
        impact="2",
        priority="3",
        category="inquiry",
        caller_id="",
        assignment_group="",
        assigned_to=""
    ):
    """
    Create an incident ticket in ServiceNow.

    Parameters:
    -----------
    short_description : str  - Brief summary of the incident (REQUIRED)
    description       : str  - Detailed description of the incident
    urgency           : str  - 1=High, 2=Medium, 3=Low
    impact            : str  - 1=High, 2=Medium, 3=Low
    priority          : str  - 1=Critical, 2=High, 3=Moderate, 4=Low, 5=Planning
    category          : str  - Category of the incident
    caller_id         : str  - sys_id or user_name of the caller
    assignment_group  : str  - Name or sys_id of the assignment group
    assigned_to       : str  - sys_id or user_name of the assigned person

    Returns:
    --------
    dict : Response containing ticket details or None on failure
    """

    url = f"{BASE_URL}/api/now/table/incident"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # ─────────────────────────────────────────────
    # Build the payload with basic fields
    # ─────────────────────────────────────────────
    payload = {
        "short_description": short_description,
        "description": description,
        "urgency": urgency,
        "impact": impact,
        "priority": priority,
        "category": category,
    }

    # Add optional fields only if provided
    if caller_id:
        payload["caller_id"] = caller_id
    if assignment_group:
        payload["assignment_group"] = assignment_group
    if assigned_to:
        payload["assigned_to"] = assigned_to

    print("\n" + "=" * 60)
    print("📝 CREATING INCIDENT TICKET")
    print("=" * 60)
    print(f"   Short Description : {short_description}")
    print(f"   Description       : {description}")
    print(f"   Urgency           : {urgency}")
    print(f"   Impact            : {impact}")
    print(f"   Priority          : {priority}")
    print(f"   Category          : {category}")
    print("-" * 60)

    try:
        response = requests.post(
            url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )

        if response.status_code == 201:
            result = response.json().get("result", {})

            ticket_number = result.get("number", "N/A")
            sys_id = result.get("sys_id", "N/A")
            state = result.get("state", "N/A")
            created_on = result.get("sys_created_on", "N/A")
            opened_by = result.get("opened_by", {})

            # Map state number to label
            state_map = {
                "1": "New",
                "2": "In Progress",
                "3": "On Hold",
                "6": "Resolved",
                "7": "Closed",
                "8": "Canceled"
            }
            state_label = state_map.get(str(state), state)

            print("\n✅ INCIDENT CREATED SUCCESSFULLY!")
            print("=" * 60)
            print(f"   🎫 Ticket Number  : {ticket_number}")
            print(f"   🔑 Sys ID         : {sys_id}")
            print(f"   📊 State          : {state_label}")
            print(f"   📅 Created On     : {created_on}")
            print(f"   🔗 URL            : {BASE_URL}/incident.do?sys_id={sys_id}")
            print("=" * 60)

            return {
                "success": True,
                "ticket_number": ticket_number,
                "sys_id": sys_id,
                "state": state_label,
                "created_on": created_on,
                "url": f"{BASE_URL}/incident.do?sys_id={sys_id}",
                "full_response": result
            }

        else:
            print(f"\n❌ FAILED TO CREATE INCIDENT")
            print(f"   Status Code : {response.status_code}")
            print(f"   Response    : {response.text}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }

    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST EXCEPTION: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_incident(ticket_number):
    """Retrieve an incident by its ticket number to verify creation."""

    url = f"{BASE_URL}/api/now/table/incident"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    params = {
        "sysparm_query": f"number={ticket_number}",
        "sysparm_limit": "1",
        "sysparm_display_value": "true"
    }

    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            results = response.json().get("result", [])
            if results:
                incident = results[0]
                print(f"\n✅ RETRIEVED INCIDENT: {ticket_number}")
                print("-" * 60)
                print(f"   Short Description : {incident.get('short_description', 'N/A')}")
                print(f"   State             : {incident.get('state', 'N/A')}")
                print(f"   Priority          : {incident.get('priority', 'N/A')}")
                print(f"   Urgency           : {incident.get('urgency', 'N/A')}")
                print(f"   Impact            : {incident.get('impact', 'N/A')}")
                print(f"   Category          : {incident.get('category', 'N/A')}")
                print(f"   Created On        : {incident.get('sys_created_on', 'N/A')}")
                print(f"   Opened By         : {incident.get('opened_by', 'N/A')}")
                print("-" * 60)
                return incident
            else:
                print(f"❌ Incident {ticket_number} not found.")
                return None
        else:
            print(f"❌ Failed to retrieve incident. Status: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error retrieving incident: {str(e)}")
        return None


def update_incident(sys_id, update_fields):
    """Update an existing incident."""

    url = f"{BASE_URL}/api/now/table/incident/{sys_id}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.patch(
            url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=headers,
            data=json.dumps(update_fields),
            timeout=30
        )

        if response.status_code == 200:
            result = response.json().get("result", {})
            print(f"\n✅ INCIDENT UPDATED SUCCESSFULLY!")
            print(f"   Ticket: {result.get('number', 'N/A')}")
            return result
        else:
            print(f"❌ Failed to update. Status: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating incident: {str(e)}")
        return None

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("🔧 SERVICENOW - UPDATE EXISTING INCIDENT")
    print("=" * 60 + "\n")

  
    if not test_connection():
        exit(1)

    #Get incident number from user
    print("\n" + "=" * 60)
    incident_number = input("🎫 Enter Incident Number (e.g., INC0010001): ").strip().upper()

    if not incident_number:
        print("❌ No incident number provided. Exiting.")
        exit(1)

    if not incident_number.startswith("INC"):
        incident_number = "INC" + incident_number

    # Retrieve the incident to get sys_id
    print(f"\n🔍 Looking up {incident_number}...")
    incident_data = get_incident(incident_number)

    if not incident_data:
        print(f"❌ Incident '{incident_number}' not found. Exiting.")
        exit(1)

    sys_id = incident_data.get("sys_id")

    # Step 5: Update with hardcoded basic details
    print(f"\n🔄 Updating {incident_number}...")

    update_fields = {
        "urgency": "1",
        "impact": "1",
        "priority": "1",
        "work_notes": "Escalated to P1 via automation script.",
        "comments": "We are actively working on this issue."
    }

    updated = update_incident(sys_id, update_fields)

    if updated:
        print("\n" + "=" * 60)
        print("🎉 UPDATE COMPLETED!")
        print(f"   🔗 {BASE_URL}/incident.do?sys_id={sys_id}")
        print("=" * 60 + "\n")
    else:
        print("\n❌ UPDATE FAILED!\n")
