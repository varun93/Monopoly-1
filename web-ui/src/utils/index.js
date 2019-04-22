export const substituteEndpoint = (endpoint, agentId, gameId) => {
  endpoint = endpoint.replace(/{%game_id%}/g, gameId);
  endpoint = endpoint.replace(/{%agent_id%}/g, agentId);
  return endpoint;
};

// https://stackoverflow.com/questions/3895478/does-javascript-have-a-method-like-range-to-generate-a-range-within-the-supp
export const range = (size, startAt = 0) => {
  return [...Array(size).keys()].map(i => i + startAt);
};

export const amIOwner = (property, myId) => {
  return property.owned === true && property.ownerId === myId;
};

export const completedMonopoly = (properties, property, myId) => {
  for (let index = 0; index < property.monopoly_group_element.length; index++) {
    if (!amIOwner(properties[index], myId)) return false;
    if (properties[index].houses > 0) return false;
  }
  return true;
};

export const getBuyingCandidates = state => {
  const { properties, myId } = state;

  const candidates = properties
    .filter(property => {
      if (property.class !== "Street") return false;
      if (!amIOwner(property, myId)) return false;
      if (!completedMonopoly(properties, property, myId)) return false;
      return true;
    })
    .map(property => property.id);

  console.log("Buying Candidates");
  console.log(candidates);

  return candidates;
};

export const getSellingCandidates = state => {
  const { properties, myId } = state;

  const candidates = properties
    .filter(property => {
      if (property.class !== "Street") return false;
      if (!amIOwner(property, myId)) return false;
      if (!completedMonopoly(properties, property, myId)) return false;
      return true;
    })
    .map(property => property.id);
  console.log("Selling Candidates");
  console.log(candidates);
  return candidates;
};

export const getMortgageCandidates = state => {
  const { properties, myId } = state;

  const candidates = properties
    .filter(property => {
      if (property.class !== "Street") return false;
      if (property.mortgaged) return false;
      if (!amIOwner(property, myId)) return false;
      if (!completedMonopoly(properties, property, myId)) {
        if (property.houses > 0 || property.hotel) return false;
      }
      return true;
    })
    .map(property => property.id);

  console.log("Mortgage Candidates");
  console.log(candidates);
  return candidates;
};
