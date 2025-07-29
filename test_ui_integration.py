"""
Test script for UI integration with enhanced game display
בדיקת אינטגרציה עם תצוגה מורחבת של המשחק
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'KFC_Py'))

from GameFactory import create_game
from GraphicsFactory import ImgFactory
from MessageBroker import game_message_broker
from GameUISubscriber import GameUISubscriber
import time

def test_enhanced_ui():
    """
    בדיקת תצוגת UI מורחבת עם טבלאות מהלכים
    """
    print("🎮 בודק אינטגרציה עם UI מורחב...")
    
    # יצירת משחק
    pieces_root = os.path.join(os.path.dirname(__file__), "pieces")
    img_factory = ImgFactory()
    game = create_game(pieces_root, img_factory)
    
    print("✅ המשחק נוצר בהצלחה!")
    print("🎯 הפעלת המשחק עם UI מורחב...")
    print("  - לוח מרכזי עם הכלי")
    print("  - צד ימין: טבלת מהלכים של הלבן") 
    print("  - צד שמאל: טבלת מהלכים של השחור")
    print("  - תצוגת ניקוד בחלק העליון")
    print("\n🎮 משתמש במקשי החצים וספקייס להזזת כלים")
    print("   הסמן יהפוך לאדום כשחייל נבחר! 🔴")
    print("   ESC ליציאה מהמשחק\n")
    
    try:
        # הרצת המשחק עם תצוגת UI מורחבת
        game.run(num_iterations=None, is_with_graphics=True)
        
    except KeyboardInterrupt:
        print("\n👋 המשחק הופסק על ידי המשתמש")
    except Exception as e:
        print(f"❌ שגיאה במהלך המשחק: {e}")
        import traceback
        traceback.print_exc()
    
    print("🎯 המשחק הסתיים!")

if __name__ == "__main__":
    test_enhanced_ui()
