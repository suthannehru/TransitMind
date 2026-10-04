template = [
    {
        "question": "",
        "expected_tools": ["parse_route_query", "find_route"],
        "expected_args": {"find_route": {"start_stop_id": "", "end_stop_id": ""}},
        "category": "routing"
    },
        {
        "question": "",
        "expected_tools": ["get_service_alerts"],
        "expected_args": {"get_service_alerts": {"line": ""}},
        "category": "service_alerts"
    },
        {
        "question": "",
        "expected_tools": ["get_live_positions"],
        "expected_args": {"get_live_positions": {"line": ""}},
        "category": "train_position"
    }
]

test_questions = [
  {
    "question": "What's the easiest way to get from Kew Gardens to Sheepshead Bay?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "F06", "end_stop_id": "D39"}},
    "category": "routing"
  },
  {
    "question": "I'm at Flushing-Main St and need to get to 34 St-Hudson Yards. What should I take?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "701", "end_stop_id": "726"}},
    "category": "routing"
  },
  {
    "question": "Need directions from Astoria-Ditmars Blvd to Union Square.",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "R01", "end_stop_id": "R20"}},
    "category": "routing"
  },
  {
    "question": "How do I go from Jamaica Center to World Trade Center?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "G05", "end_stop_id": "E01"}},
    "category": "routing"
  },
  {
    "question": "Get me from Coney Island-Stillwell Av to Sheepshead Bay.",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "D43", "end_stop_id": "D39"}},
    "category": "routing"
  },
  {
    "question": "What's the route from Bedford Av to 8 Av?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "L08", "end_stop_id": "L01"}},
    "category": "routing"
  },
  {
    "question": "How would I travel from Pelham Bay Park to Brooklyn Bridge-City Hall?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "601", "end_stop_id": "640"}},
    "category": "routing"
  },
  {
    "question": "I need to get from Far Rockaway-Mott Av to World Trade Center.",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "H11", "end_stop_id": "E01"}},
    "category": "routing"
  },
  {
    "question": "Which way do I go from Woodlawn to Bowling Green?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "401", "end_stop_id": "420"}},
    "category": "routing"
  },
  {
    "question": "Can you find me a route from Kew Gardens to World Trade Center?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "F06", "end_stop_id": "E01"}},
    "category": "routing"
  },
  {
    "question": "How can I get from Flushing-Main St to Mets-Willets Point?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "701", "end_stop_id": "705"}},
    "category": "routing"
  },
  {
    "question": "Im trying to get from Kew Gardens to Sheepshed Bay. Which way should I go?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "F06", "end_stop_id": "D39"}},
    "category": "routing"
  },
  {
    "question": "Route me from Brighton Beach down to Coney Island-Stillwell Av.",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "D40", "end_stop_id": "D43"}},
    "category": "routing"
  },
  {
    "question": "How do I get from Lexington Av/63 St to 72 St on the Q?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "B08", "end_stop_id": "Q03"}},
    "category": "routing"
  },
  {
    "question": "Whats the best way from Sheepshead Bay to Brighton Beach?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "D39", "end_stop_id": "D40"}},
    "category": "routing"
  },
  {
    "question": "How do I get from 34 St-Hudson Yards to Flushing-Main St?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "726", "end_stop_id": "701"}},
    "category": "routing"
  },
  {
    "question": "What's the best way from Jamaica Center to Kew Gardens?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "G05", "end_stop_id": "F06"}},
    "category": "routing"
  },
  {
    "question": "Can you route me from 8 Av to Bedford Av?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "L01", "end_stop_id": "L08"}},
    "category": "routing"
  },
  {
    "question": "Need to get from Sheepshead Bay to Lexington Av/63 St.",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "D39", "end_stop_id": "B08"}},
    "category": "routing"
  },
  {
    "question": "How do I travel from World Trade Center to Kew Gardens?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "E01", "end_stop_id": "F06"}},
    "category": "routing"
  },
  {
    "question": "Find me a route from Brighton Beach to 72 St.",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "D40", "end_stop_id": "Q03"}},
    "category": "routing"
  },
  {
    "question": "I'm at Mets-Willets Point. How do I get back to Flushing-Main St?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "705", "end_stop_id": "701"}},
    "category": "routing"
  },
  {
    "question": "Take me from Bowling Green to Woodlawn.",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "420", "end_stop_id": "401"}},
    "category": "routing"
  },
  {
    "question": "Whats the route from Pelham Bay Park to Bowling Green?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "601", "end_stop_id": "420"}},
    "category": "routing"
  },
  {
    "question": "How can I get from Far Rockaway-Mott Av to Kew Gardens?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "H11", "end_stop_id": "F06"}},
    "category": "routing"
  },
  {
    "question": "How do I get from St George to Tottenville?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "S31", "end_stop_id": "S09"}},
    "category": "routing"
  },
  {
    "question": "What's the quickest way from Tompkinsville to Great Kills?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "S30", "end_stop_id": "S19"}},
    "category": "routing"
  },
  {
    "question": "I'm at Clifton. How do I get to Huguenot?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "S28", "end_stop_id": "S16"}},
    "category": "routing"
  },
  {
    "question": "Need to get from Great Kills to Arthur Kill.",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "S19", "end_stop_id": "S11"}},
    "category": "routing"
  },
  {
    "question": "Im at New Dorp and trying to get to St George.",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {"find_route": {"start_stop_id": "S22", "end_stop_id": "S31"}},
    "category": "routing"
  },

  {
    "question": "Is the 1 train delayed right now?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "1"}},
    "category": "service_alerts"
  },
  {
    "question": "Anything going on with the 2 line today?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "2"}},
    "category": "service_alerts"
  },
  {
    "question": "How's the 3 running this morning?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "3"}},
    "category": "service_alerts"
  },
  {
    "question": "Should I expect any trouble on the 4?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "4"}},
    "category": "service_alerts"
  },
  {
    "question": "What's the current service status for the 5?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "5"}},
    "category": "service_alerts"
  },
  {
    "question": "Are 6 trains running normally?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "6"}},
    "category": "service_alerts"
  },
  {
    "question": "Any service changes on the 7?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "7"}},
    "category": "service_alerts"
  },
  {
    "question": "Is something wrong with the A today?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "A"}},
    "category": "service_alerts"
  },
  {
    "question": "Check if the B has any delays.",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "B"}},
    "category": "service_alerts"
  },
  {
    "question": "How's C train service this afternoon?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "C"}},
    "category": "service_alerts"
  },
  {
    "question": "Any disruptions on the D?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "D"}},
    "category": "service_alerts"
  },
  {
    "question": "Do E trains have any issues right now?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "E"}},
    "category": "service_alerts"
  },
  {
    "question": "Im taking the F today. Any alrts?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "F"}},
    "category": "service_alerts"
  },
  {
    "question": "Has the G been having service problems?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "G"}},
    "category": "service_alerts"
  },
  {
    "question": "What's happening with J service?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "J"}},
    "category": "service_alerts"
  },
  {
    "question": "Is the L running okay tonight?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "L"}},
    "category": "service_alerts"
  },
  {
    "question": "Any problems reported on the M?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "M"}},
    "category": "service_alerts"
  },
  {
    "question": "Tell me if the N is delayd.",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "N"}},
    "category": "service_alerts"
  },
  {
    "question": "Are Q trains on schedule today?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "Q"}},
    "category": "service_alerts"
  },
  {
    "question": "What's going on with the R right now?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "R"}},
    "category": "service_alerts"
  },
  {
    "question": "Any W train alerts this evening?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "W"}},
    "category": "service_alerts"
  },
  {
    "question": "Is the Z line dealing with any delays?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "Z"}},
    "category": "service_alerts"
  },
  {
    "question": "How's the Staten Island Railway running today?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "SI"}},
    "category": "service_alerts"
  },
  {
    "question": "Any curent SIR service disruptions?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "SI"}},
    "category": "service_alerts"
  },
  {
    "question": "Should I expect Staten Island Railway delays this morning?",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {"get_service_alerts": {"line": "SI"}},
    "category": "service_alerts"
  },

  {
    "question": "Where are the 1 trains right now?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "1"}},
    "category": "train_position"
  },
  {
    "question": "Show me the current locations of the 2 trains.",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "2"}},
    "category": "train_position"
  },
  {
    "question": "Can I see where the 3 trains are?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "3"}},
    "category": "train_position"
  },
  {
    "question": "What's the live position of the 4 trains?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "4"}},
    "category": "train_position"
  },
  {
    "question": "Track the 5 trains for me.",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "5"}},
    "category": "train_position"
  },
  {
    "question": "Where along the line are the 6 trains?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "6"}},
    "category": "train_position"
  },
  {
    "question": "Any 7 trains around Queens right now?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "7"}},
    "category": "train_position"
  },
  {
    "question": "I'd like to see the live A train locations.",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "A"}},
    "category": "train_position"
  },
  {
    "question": "Which part of the route are the B trains on right now?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "B"}},
    "category": "train_position"
  },
  {
    "question": "Can you locate the C trains for me?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "C"}},
    "category": "train_position"
  },
  {
    "question": "Show where the D trains are at the moment.",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "D"}},
    "category": "train_position"
  },
  {
    "question": "Whereabouts are the E trains?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "E"}},
    "category": "train_position"
  },
  {
    "question": "Give me the curent F train positons.",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "F"}},
    "category": "train_position"
  },
  {
    "question": "Do you know where the G trains currently are?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "G"}},
    "category": "train_position"
  },
  {
    "question": "Pull up the live J train locations.",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "J"}},
    "category": "train_position"
  },
  {
    "question": "Where on the L line are the trains right now?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "L"}},
    "category": "train_position"
  },
  {
    "question": "Can you tell me the current position of M trains?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "M"}},
    "category": "train_position"
  },
  {
    "question": "I want to know were the N trains are.",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "N"}},
    "category": "train_position"
  },
  {
    "question": "What are the live locations for Q trains?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "Q"}},
    "category": "train_position"
  },
  {
    "question": "Where can I find the R trains currently running?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "R"}},
    "category": "train_position"
  },
  {
    "question": "Show me where the W trains are.",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "W"}},
    "category": "train_position"
  },
  {
    "question": "Where are the Z trains at the moment?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "Z"}},
    "category": "train_position"
  },
  {
    "question": "Where are the SIR trains right now?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "SI"}},
    "category": "train_position"
  },
  {
    "question": "Show me the curent Staten Island Railway train locations.",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "SI"}},
    "category": "train_position"
  },
  {
    "question": "Any SIR trains near Great Kills at the moment?",
    "expected_tools": ["get_live_positions"],
    "expected_args": {"get_live_positions": {"line": "SI"}},
    "category": "train_position"
  },

  {
    "question": "How do I go from Kew Gardens to Sheepshead Bay, and are there any issues on the F?",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts"],
    "expected_args": {
      "find_route": {"start_stop_id": "F06", "end_stop_id": "D39"},
      "get_service_alerts": {"line": "F"}
    },
    "category": "routing_service_alerts"
  },
  {
    "question": "I'm heading from Flushing-Main St to 34 St-Hudson Yards. What's the route, and is the 7 running normally?",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts"],
    "expected_args": {
      "find_route": {"start_stop_id": "701", "end_stop_id": "726"},
      "get_service_alerts": {"line": "7"}
    },
    "category": "routing_service_alerts"
  },
  {
    "question": "Get me from Jamaica Center to World Trade Center and let me know if the E has any problems.",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts"],
    "expected_args": {
      "find_route": {"start_stop_id": "G05", "end_stop_id": "E01"},
      "get_service_alerts": {"line": "E"}
    },
    "category": "routing_service_alerts"
  },
  {
    "question": "Whats the best way from St George to Totenvile, and are there any SIR delys?",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts"],
    "expected_args": {
      "find_route": {"start_stop_id": "S31", "end_stop_id": "S09"},
      "get_service_alerts": {"line": "SI"}
    },
    "category": "routing_service_alerts"
  },
  {
    "question": "Can you route me from Astoria-Ditmars Blvd to Union Square and check whether the N has service changes?",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts"],
    "expected_args": {
      "find_route": {"start_stop_id": "R01", "end_stop_id": "R20"},
      "get_service_alerts": {"line": "N"}
    },
    "category": "routing_service_alerts"
  },

  {
    "question": "How do I get from Flushing-Main St to Mets-Willets Point, and where are the 7 trains right now?",
    "expected_tools": ["parse_route_query", "find_route", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "701", "end_stop_id": "705"},
      "get_live_positions": {"line": "7"}
    },
    "category": "routing_train_position"
  },
  {
    "question": "Route me from Bedford Av to 8 Av and show me where the L trains are.",
    "expected_tools": ["parse_route_query", "find_route", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "L08", "end_stop_id": "L01"},
      "get_live_positions": {"line": "L"}
    },
    "category": "routing_train_position"
  },
  {
    "question": "Im trying to go from St George to Great Kils. Whats the route and where are the SIR trains curently?",
    "expected_tools": ["parse_route_query", "find_route", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "S31", "end_stop_id": "S19"},
      "get_live_positions": {"line": "SI"}
    },
    "category": "routing_train_position"
  },
  {
    "question": "What's my route from Coney Island-Stillwell Av to Sheepshead Bay, and can you show me the Q train locations?",
    "expected_tools": ["parse_route_query", "find_route", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "D43", "end_stop_id": "D39"},
      "get_live_positions": {"line": "Q"}
    },
    "category": "routing_train_position"
  },
  {
    "question": "Need directions from Pelham Bay Park to Brooklyn Bridge-City Hall, plus the current positions of the 6 trains.",
    "expected_tools": ["parse_route_query", "find_route", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "601", "end_stop_id": "640"},
      "get_live_positions": {"line": "6"}
    },
    "category": "routing_train_position"
  },

  {
    "question": "Is the A delayed, and where are the A trains right now?",
    "expected_tools": ["get_service_alerts", "get_live_positions"],
    "expected_args": {
      "get_service_alerts": {"line": "A"},
      "get_live_positions": {"line": "A"}
    },
    "category": "service_alerts_train_position"
  },
  {
    "question": "Anything wrong with the 7 today, and can you show me where the trains are?",
    "expected_tools": ["get_service_alerts", "get_live_positions"],
    "expected_args": {
      "get_service_alerts": {"line": "7"},
      "get_live_positions": {"line": "7"}
    },
    "category": "service_alerts_train_position"
  },
  {
    "question": "Hows SIR service looking and were are the Staten Island Railway trains curently?",
    "expected_tools": ["get_service_alerts", "get_live_positions"],
    "expected_args": {
      "get_service_alerts": {"line": "SI"},
      "get_live_positions": {"line": "SI"}
    },
    "category": "service_alerts_train_position"
  },
  {
    "question": "Are F trains having problems, and what are their live locations?",
    "expected_tools": ["get_service_alerts", "get_live_positions"],
    "expected_args": {
      "get_service_alerts": {"line": "F"},
      "get_live_positions": {"line": "F"}
    },
    "category": "service_alerts_train_position"
  },
  {
    "question": "Check the L status and tell me where the trains are along the line.",
    "expected_tools": ["get_service_alerts", "get_live_positions"],
    "expected_args": {
      "get_service_alerts": {"line": "L"},
      "get_live_positions": {"line": "L"}
    },
    "category": "service_alerts_train_position"
  },

  {
    "question": "How do I get from Flushing-Main St to Mets-Willets Point, are there any 7 train delays, and where are the trains right now?",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "701", "end_stop_id": "705"},
      "get_service_alerts": {"line": "7"},
      "get_live_positions": {"line": "7"}
    },
    "category": "routing_service_alerts_train_position"
  },
  {
    "question": "Im going from St George to Tottenvile. Give me the route, check SIR servce, and show me were the trains are.",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "S31", "end_stop_id": "S09"},
      "get_service_alerts": {"line": "SI"},
      "get_live_positions": {"line": "SI"}
    },
    "category": "routing_service_alerts_train_position"
  },
  {
    "question": "Plan my trip from Bedford Av to 8 Av, tell me if the L has disruptions, and show its live train positions.",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "L08", "end_stop_id": "L01"},
      "get_service_alerts": {"line": "L"},
      "get_live_positions": {"line": "L"}
    },
    "category": "routing_service_alerts_train_position"
  },
  {
    "question": "What's the route from Far Rockaway-Mott Av to World Trade Center? Also check the A for issues and tell me where the A trains are.",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "H11", "end_stop_id": "E01"},
      "get_service_alerts": {"line": "A"},
      "get_live_positions": {"line": "A"}
    },
    "category": "routing_service_alerts_train_position"
  },
  {
    "question": "I need to travel from Great Kills to St George. What's the route, is SIR running okay, and where are the trains?",
    "expected_tools": ["parse_route_query", "find_route", "get_service_alerts", "get_live_positions"],
    "expected_args": {
      "find_route": {"start_stop_id": "S19", "end_stop_id": "S31"},
      "get_service_alerts": {"line": "SI"},
      "get_live_positions": {"line": "SI"}
    },
    "category": "routing_service_alerts_train_position"
  },

  {
    "question": "How much does it cost to ride the NYC subway?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Can I use Apple Pay to enter the subway?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "How does OMNY work on the MTA subway?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Whats the difference between an express and local subway train?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Does the NYC subway run 24 hours?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Can I bring my bike onto the subway?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Are dogs allowed on MTA subway trains?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Do subway stations have bathrooms?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Can I still buy a MetroCard?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "How does the OMNY weekly fare cap work?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Why do some NYC subway trains run express?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Which MTA subway lines use newer trains?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Do kids ride the subway for free?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "What do the different subway colors mean?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },
  {
    "question": "Why are some subway stations not wheelchair accessible?",
    "expected_tools": [],
    "expected_args": {},
    "category": "no_tools"
  },

  {
    "question": "Kew Gardens Sheepshead Bay how do I get there",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {
      "find_route": {"start_stop_id": "F06", "end_stop_id": "D39"}
    },
    "category": "messy_input"
  },
  {
    "question": "St George Tottenvile route please",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {
      "find_route": {"start_stop_id": "S31", "end_stop_id": "S09"}
    },
    "category": "messy_input"
  },
  {
    "question": "need to go Flushing-Main St Mets-Willets Point",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {
      "find_route": {"start_stop_id": "701", "end_stop_id": "705"}
    },
    "category": "messy_input"
  },
  {
    "question": "how get from Bedford Av 8 Av",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {
      "find_route": {"start_stop_id": "L08", "end_stop_id": "L01"}
    },
    "category": "messy_input"
  },
  {
    "question": "Jamaica Center World Trade Center best way?",
    "expected_tools": ["parse_route_query", "find_route"],
    "expected_args": {
      "find_route": {"start_stop_id": "G05", "end_stop_id": "E01"}
    },
    "category": "messy_input"
  },
  {
    "question": "How do I get to Sheepshead Bay?",
    "expected_tools": [],
    "expected_args": {},
    "category": "messy_input"
  },
  {
    "question": "How do I get from Kew Gardens?",
    "expected_tools": [],
    "expected_args": {},
    "category": "messy_input"
  },
  {
    "question": "Need a route to World Trade Center",
    "expected_tools": [],
    "expected_args": {},
    "category": "messy_input"
  },
  {
    "question": "I'm at St George how do I get there?",
    "expected_tools": [],
    "expected_args": {},
    "category": "messy_input"
  },
  {
    "question": "is the F having any problems",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {
      "get_service_alerts": {"line": "F"}
    },
    "category": "messy_input"
  },
  {
    "question": "7 train any delys today",
    "expected_tools": ["get_service_alerts"],
    "expected_args": {
      "get_service_alerts": {"line": "7"}
    },
    "category": "messy_input"
  },
  {
    "question": "Are there any train delays right now?",
    "expected_tools": [],
    "expected_args": {},
    "category": "messy_input"
  },
  {
    "question": "where the A trains at",
    "expected_tools": ["get_live_positions"],
    "expected_args": {
      "get_live_positions": {"line": "A"}
    },
    "category": "messy_input"
  },
  {
    "question": "SIR trains where are they rn",
    "expected_tools": ["get_live_positions"],
    "expected_args": {
      "get_live_positions": {"line": "SI"}
    },
    "category": "messy_input"
  },
  {
    "question": "Where are the trains right now?",
    "expected_tools": [],
    "expected_args": {},
    "category": "messy_input"
  }
]


