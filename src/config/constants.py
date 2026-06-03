# =====================================================
# FEATURE WEIGHTS
# =====================================================

FEATURE_WEIGHTS = {

    "internalTopics": 3.5,

    "learningPath": 3.0,

    "relatedDomains": 2.5,

    "domain": 2.0,

    "team": 1.5,

    "securityType": 1.5,

    "technologies": 1.2,

    "tools": 1.0,

    "tags": 1.0,

    "difficultyScore": 0.8,

    "popularityScore": 0.4,

    "price": 0.1
}


# =====================================================
# DOMAIN BOOSTS
# =====================================================

DOMAIN_BOOSTS = {

    "cloud-security": 0.35,

    "red-team": 0.25,

    "web-security": 0.20,

    "blue-team": 0.15,

    "purple-team": 0.15,

    "ethical-hacking": 0.15,

    "devops-security": 0.20
}


# =====================================================
# LEARNING PROGRESSION
# =====================================================

PROGRESSION_MAP = {

    "beginner": 1,

    "intermediate": 2,

    "advanced": 3
}


# =====================================================
# RERANK BOOSTS
# =====================================================

SAME_DOMAIN_BOOST = 1.2

SECURITY_ALIGNMENT_BOOST = 1.0

TOPIC_OVERLAP_BOOST = 1.5

LEARNING_PATH_BOOST = 1.3

CLOUD_SPECIALIZATION_BOOST = 1.4

DIFFICULTY_PROGRESSION_BOOST = 0.8

POPULARITY_BOOST = 0.2

DIVERSITY_PENALTY = 0.3


# =====================================================
# DEFAULTS
# =====================================================

DEFAULT_POPULARITY_SCORE = 50

DEFAULT_TOP_K = 10

DEFAULT_KMEANS_CLUSTERS = 8