export const substituteEndpoint = (endpoint, agentId, gameId) => {
  endpoint = endpoint.replace(/{%game_id%}/g, gameId);
  endpoint = endpoint.replace(/{%agent_id%}/g, agentId);
  return endpoint;
};
