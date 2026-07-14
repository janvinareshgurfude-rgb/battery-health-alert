#!/usr/bin/env bash
DITTO_BASE="${DITTO_BASE:-http://localhost:8080}"
DITTO_USER="${DITTO_USER:-ditto}"
DITTO_PASS="${DITTO_PASS:-ditto}"
THING_ID="${DITTO_THING_ID:-hag:vehicle-01}"
POLICY_ID="${THING_ID}"

echo "Creating policy ${POLICY_ID} ..."
curl -s -u "${DITTO_USER}:${DITTO_PASS}" -X PUT \
  "${DITTO_BASE}/api/2/policies/${POLICY_ID}" \
  -H "Content-Type: application/json" \
  -d '{"entries":{"owner":{"subjects":{"nginx:ditto":{"type":"nginx basic auth user"}},"resources":{"thing:/":{"grant":["READ","WRITE"],"revoke":[]},"policy:/":{"grant":["READ","WRITE"],"revoke":[]},"message:/":{"grant":["READ","WRITE"],"revoke":[]}}}}}'

echo
echo "Creating thing ${THING_ID} ..."
curl -s -u "${DITTO_USER}:${DITTO_PASS}" -X PUT \
  "${DITTO_BASE}/api/2/things/${THING_ID}" \
  -H "Content-Type: application/json" \
  -d "{\"policyId\":\"${POLICY_ID}\",\"attributes\":{\"vehicleName\":\"HAG demo vehicle\"},\"features\":{\"battery\":{\"properties\":{\"soc\":100,\"batteryAlert\":false,\"lastUpdated\":0}}}}"

echo
echo "Done. Verify with:"
echo "  curl -u ${DITTO_USER}:${DITTO_PASS} ${DITTO_BASE}/api/2/things/${THING_ID}"
