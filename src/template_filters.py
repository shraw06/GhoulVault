def pretty_rank(rank: str):
    match rank:
        case "special":
            return "Special Class"
        case "associate":
            return "Associate Special Class"
        case "first":
            return "First Class"
        case "1":
            return "Rank 1"
        case "2":
            return "Rank 2"
        case "3":
            return "Rank 3"
        case _:
            return "Unknown Rank"
