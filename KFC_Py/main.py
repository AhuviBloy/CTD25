
import logging
from GameFactory import create_game
from GraphicsFactory import ImgFactory

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Import test events to register handlers
    import test_events
    
    game = create_game("../pieces", ImgFactory())
    game.run()

