import personal
from artifacts import ArtifactsClient   # or AsyncArtifactsClient

with ArtifactsClient(token=personal.TOKEN) as client:
    char = client.character(personal.CHARACTER_NAME)

    char.move(x=0, y=1)          # auto-waits
    result = char.fight()        # auto-waits
    print(result.fight.result)
