from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

ERP_Project = {
    'Team Lead': ["RamaKrisha"],
    'Pushpak_Team': ["Pushpak", "siddhartha", "Venu", "Shanmukh", "Krishna manikanta"],
    'jagdesh_Team': ["jagdesh", "sriaram", "Vamshidar", "Susheela", "Poojitha"]
}



@app.get("/project")
def get_project(team_name: str = Query(None, description="Enter a team name")):
    if team_name:
        team = ERP_Project.get(team_name)
        if team:
            return {team_name: team}
        return {"error": f"Team '{team_name}' not found"}
    return ERP_Project



class TeamUpdate(BaseModel):
    members: list[str]

@app.put("/project/{team_name}")
def update_team(team_name: str, update: TeamUpdate):
    if team_name in ERP_Project:
        ERP_Project[team_name] = update.members
        return {"message": f"{team_name} updated successfully", team_name: update.members}
    return {"error": f"Team '{team_name}' not found"}