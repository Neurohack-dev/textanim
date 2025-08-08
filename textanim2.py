import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import tempfile
import os

def create_text_animation_gif(background_image, text_segments, duration_per_frame, font_size_multiplier, output_path):
    """
    Crée un GIF animé avec du texte qui change sur une image de fond
    """
    frames = []
    
    # Redimensionner l'image de fond à une taille raisonnable pour le GIF
    max_size = (800, 600)
    background_image.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Essayer différentes polices
    try:
        # Taille de police basée sur la taille de l'image (augmentée et personnalisable)
        base_font_size = min(background_image.size) // 8  # Taille de base plus grande
        font_size = int(base_font_size * font_size_multiplier)  # Appliquer le multiplicateur
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except:
                font = ImageFont.load_default()
    
    for text in text_segments:
        if text.strip():  # Ignorer les segments vides
            # Créer une copie de l'image de fond
            frame = background_image.copy()
            draw = ImageDraw.Draw(frame)
            
            # Calculer la position du texte pour le centrer
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (frame.width - text_width) // 2
            y = (frame.height - text_height) // 2
            
            # Dessiner un rectangle semi-transparent derrière le texte pour la lisibilité
            padding = 10
            rect_coords = [
                x - padding,
                y - padding,
                x + text_width + padding,
                y + text_height + padding
            ]
            draw.rectangle(rect_coords, fill=(0, 0, 0, 128))
            
            # Dessiner le texte en blanc
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            frames.append(frame)
    
    # Sauvegarder le GIF
    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=int(duration_per_frame * 1000),  # Convertir en millisecondes
            loop=0
        )
        return True
    return False

def main():
    st.title("🎬 Générateur d'Animation Texte sur Image")
    st.write("Créez des animations GIF avec du texte progressif sur vos images !")
    
    # Section upload d'image
    st.header("📸 Image de fond")
    uploaded_file = st.file_uploader(
        "Choisissez une image de fond",
        type=['png', 'jpg', 'jpeg'],
        help="Formats supportés: PNG, JPG, JPEG"
    )
    
    if uploaded_file is not None:
        # Afficher l'image uploadée
        image = Image.open(uploaded_file)
        st.image(image, caption="Image de fond", use_column_width=True)
        
        # Section configuration du texte
        st.header("✏️ Configuration du texte")
        
        # Méthode de saisie du texte
        input_method = st.radio(
            "Comment voulez-vous saisir votre texte ?",
            ["Saisie manuelle par segments", "Phrase complète à découper"]
        )
        
        text_segments = []
        
        if input_method == "Saisie manuelle par segments":
            st.write("Saisissez chaque segment de texte dans une case séparée :")
            
            # Nombre de segments
            num_segments = st.number_input(
                "Nombre de segments",
                min_value=1,
                max_value=20,
                value=4,
                help="Nombre de groupes de mots à afficher"
            )
            
            # Cases de saisie pour chaque segment
            for i in range(num_segments):
                segment = st.text_input(
                    f"Segment {i+1}",
                    key=f"segment_{i}",
                    placeholder=f"Ex: {'j\'aime bien' if i==0 else 'regarder' if i==1 else 'mon chat' if i==2 else 'manger'}"
                )
                if segment:
                    text_segments.append(segment)
        
        else:  # Phrase complète à découper
            full_text = st.text_area(
                "Saisissez votre phrase complète",
                placeholder="Ex: j'aime bien - regarder - mon chat - manger",
                help="Utilisez ' - ' pour séparer les segments"
            )
            
            if full_text:
                # Découper la phrase
                text_segments = [segment.strip() for segment in full_text.split(' - ') if segment.strip()]
                
                st.write("**Aperçu des segments :**")
                for i, segment in enumerate(text_segments, 1):
                    st.write(f"{i}. {segment}")
        
        # Configuration temporelle
        st.header("⏱️ Configuration de l'animation")
        
        # Configuration de la taille de police
        st.subheader("📝 Taille du texte")
        font_size_multiplier = st.slider(
            "Taille de la police",
            min_value=0.5,
            max_value=3.0,
            value=1.5,
            step=0.1,
            help="Multiplie la taille de base de la police (1.0 = taille normale, 2.0 = deux fois plus grand)"
        )
        
        duration = st.slider(
            "Durée d'affichage par segment (secondes)",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            step=0.5,
            help="Temps pendant lequel chaque segment reste affiché"
        )
        
        # Aperçu de l'animation
        if text_segments:
            st.header("👀 Aperçu")
            total_duration = len(text_segments) * duration
            st.info(f"Votre animation contiendra {len(text_segments)} segments et durera {total_duration} secondes au total.")
            
            # Afficher la liste des segments
            st.write("**Segments qui seront affichés :**")
            for i, segment in enumerate(text_segments, 1):
                st.write(f"{i}. \"{segment}\" ({duration}s)")
        
        # Bouton de génération
        if st.button("🎬 Générer l'animation GIF", type="primary"):
            if not text_segments:
                st.error("Veuillez saisir au moins un segment de texte.")
            else:
                with st.spinner("Génération de l'animation en cours..."):
                    # Créer un fichier temporaire pour le GIF
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.gif') as tmp_file:
                        success = create_text_animation_gif(
                            image,
                            text_segments,
                            duration,
                            font_size_multiplier,
                            tmp_file.name
                        )
                        
                        if success:
                            # Lire le fichier GIF généré
                            with open(tmp_file.name, 'rb') as f:
                                gif_data = f.read()
                            
                            # Afficher le GIF
                            st.success("Animation générée avec succès !")
                            st.image(gif_data, caption="Votre animation GIF")
                            
                            # Bouton de téléchargement
                            st.download_button(
                                label="📥 Télécharger le GIF",
                                data=gif_data,
                                file_name="animation_texte.gif",
                                mime="image/gif"
                            )
                            
                            # Nettoyer le fichier temporaire
                            os.unlink(tmp_file.name)
                        else:
                            st.error("Erreur lors de la génération de l'animation.")
    
    else:
        st.info("👆 Commencez par uploader une image de fond pour créer votre animation.")
    
    # Informations d'aide
    with st.expander("💡 Conseils d'utilisation"):
        st.write("""
        **Conseils pour de meilleures animations :**
        
        - **Images :** Utilisez des images avec des zones relativement uniformes au centre pour une meilleure lisibilité du texte
        - **Texte :** Gardez vos segments courts et impactants (3-5 mots maximum)
        - **Durée :** 2 secondes par segment est généralement un bon équilibre
        - **Format :** Les images au format paysage (16:9) fonctionnent bien pour les animations
        
        **Exemples de découpage :**
        - "j'aime bien - regarder - mon chat - manger"
        - "bonjour - tout le monde - comment - ça va ?"
        - "bienvenue - sur mon - site web"
        """)

if __name__ == "__main__":
    main()
