from PIL import Image, ImageDraw, ImageFont

import discord
import io
import os
import requests
import random
import csv

from helpers import db_manager

#BASE_LOCATION = 'C:/Users/Silas/OneDrive/Documenten/GitHub/WhereContextBot3/media/images/'
BASE_LOCATION = 'media/images/'

class LeaderboardBuilder:
    def __init__(self, bot) -> None:
        self.bot = bot

        self.podium_builder = PodiumBuilder(bot)



    async def get_top_leaderboard(self, leaderboard, command):
        #  load background
        bg = Image.open(f"{BASE_LOCATION}leaderboard/LeaderboardTop.png")
        bg = bg.convert('RGBA')

        # load fonts
        fontb = ImageFont.truetype(f"{BASE_LOCATION}../fonts/contb.ttf", size=150)

        # create object for drawing
        draw = ImageDraw.Draw(bg)

        podiums = []

        # add places 1-5
        for i, stat in enumerate(leaderboard):
            
            # get user info
            user_id, count = tuple(stat)

            # normalize count
            count = human_format(count)
            
            # is podium, save info for later
            if i < 3:       
                podiums.append((user_id, count))

        # add podium
        podium_image = await self.podium_builder.get_all_podiums_image([pod[0] for pod in podiums], False, color=(62,62,62), add_characters=True)
        podium_image = resize_image(podium_image, 2000, 1800)
        remaining_width = bg.width - podium_image.width

        bg.paste(podium_image, (remaining_width//2, bg.height - podium_image.height - 150), podium_image)
    
        # draw title    
        draw.text(
            (1330, 245),
            text=command,
            align='center', font=fontb, anchor='mm', fill=(255, 104, 1)
        )

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        bg.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'leaderboardtop.png')
    


    async def get_bottom_leaderboard(self, leaderboard):
        #  load background
        bg = Image.open(f"{BASE_LOCATION}leaderboard/LeaderboardBottom.png")

        # load fonts
        fontm = ImageFont.truetype(f"{BASE_LOCATION}../fonts/contm.ttf", size=120)

        # create object for drawing
        draw = ImageDraw.Draw(bg)

        # add places 4-8
        for i, stat in enumerate(leaderboard):
            
            # get user info
            user_id, count = tuple(stat)
            user = await self.bot.fetch_user(int(user_id))
            # normalize count
            count = human_format(count)
            
            # profile picture
            pfp = Image.open(requests.get(user.display_avatar.url, stream=True).raw)
            pfp = pfp.resize((240, 240))
            bg.paste(pfp, (530, 330 + i*340))

            # username
            name = user.display_name if len(user.display_name) <= 16 else user.display_name[:13] + '...'
            draw.text(
                (1275, 420 + i*340), 
                text=name, 
                align='center', font=fontm, anchor='mm', fill=(255, 104, 1)
            )
            # count
            draw.text(
                (2050, 440 + i*340), 
                text=str(count), 
                align='center', font=fontm, anchor='mm', fill=(255, 104, 1)
            )


        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        bg.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'leaderboardbottom.png')
    
    

class CharacterBuilder:
    def __init__(self, bot):
        self.bot = bot



    def get_extra_data(self, user_id):
        # check if extra data exists
        if not os.path.exists(f"{BASE_LOCATION}{str(user_id)}/PodiumData.csv"):
            return {}

        with open(f"{BASE_LOCATION}{str(user_id)}/PodiumData.csv") as f:
            reader = csv.DictReader(f, delimiter=",")
            data = list(reader)[0]

            # make badge paste coords correct format
            coords = data["badgePasteCoords"].split(";")
            data["badgePasteCoords"] = [
                (int(coords[0]), int(coords[1])),
                (int(coords[2]), int(coords[3])),
                (int(coords[4]), int(coords[5])),
            ]

            # make pose offset correct format
            if data["poseOffset"] == "None":
                del data["poseOffset"]
            else:
                offsets = data["poseOffset"].split(";")
                data["poseOffset"] = [
                    (int(offsets[0]), int(offsets[1])),
                    (int(offsets[2]), int(offsets[3])),
                    (int(offsets[4]), int(offsets[5])),
                ]

        return data



    async def add_character_to_podium(self, podium_image, user_id, poseNumber, place):
        # get object that contains info about the arts done
        defined_art = self.get_extra_data(user_id)

        # get location of the character
        if os.path.exists(self.get_pose_location(user_id, poseNumber)):
            custom_character_location = f"{BASE_LOCATION}{str(user_id)}/Pose{poseNumber}.png"
        else:
            custom_character_location = f"{BASE_LOCATION}default/Pose{poseNumber}.png"

        # load the character image
        character_image = Image.open(custom_character_location)
        
        # resize it
        character_image = resize_image(character_image, 700)

        # create empty bg to add podium and character to
        bg = Image.new('RGBA', (podium_image.width, podium_image.height + character_image.height))
        
        # paste podium
        bg.paste(podium_image, (0, character_image.height), podium_image)

        # paste character
        offset = defined_art.get("poseOffset", [(0, 110), (0, 200), (0, 370)])[place-1]
        bg.paste(
            character_image,
            ((bg.width - character_image.width)//2 + offset[0], offset[1]), 
            character_image
        )

        # paste badge to fix 3d realness of character standing on podium
        paste_coords = defined_art.get(
            "badgePasteCoords", 
            [(255, 1050), (255, 1130), (255, 1320)]
        )
        badge_image = Image.open(f"{BASE_LOCATION}badges/Badge{place}.png")
        bg.paste(badge_image, paste_coords[place-1], badge_image)

        return bg
    


    def get_amount_of_poses(self, user_id):
        # user does not have custom pose, so default 5 poses
        if not self.has_custom_poses(user_id, 1):
            return 5
        
        i = 2 # start at 2 since we already checked pose 1
        while self.has_custom_poses(user_id, i):
            i+=1

        return i-1
    


    async def get_all_poses_image(self, user_id):

        # prerenderd of default all poses
        if not self.has_custom_poses(user_id, 1):
            return discord.File(
                f"{BASE_LOCATION}default/AllPoses.png",
                'poses.png'
            ) 
        
        # prerendered of custom all poses
        if self.has_prerender_of_poses(user_id):
            return discord.File(
                f"{BASE_LOCATION}{str(user_id)}/AllPoses.png",
                "poses.png"
            )
        
        # not prerendered, create it
        poses = [
            remove_transparency(Image.open(self.get_pose_location(user_id, i+1)))
            for i in range(self.get_amount_of_poses(user_id))
        ]

        # build poses in groups of n
        # determine n
        if len(poses)%5==0 or len(poses) > 15:
            chunksize = 5
        elif len(poses)%4==0 or len(poses) > 9:
            chunksize = 4
        else:
            chunksize = 3

        i = 0
        poses_dst = []
        # build list of groups of poses
        while len(poses) >= chunksize:
            poses_to_build = poses[:chunksize]
            poses = poses[chunksize:]

            # build poses image with n poses
            dst = get_concat_h_multi_blank(poses_to_build, 150)
            bg = self.add_numbering_to_poses(dst, i, chunksize, 150)
            
            poses_dst.append(bg)

            i += chunksize


        # leftover poses
        if len(poses) > 0:
            dst = get_concat_h_multi_blank(poses, 150)
            bg = self.add_numbering_to_poses(dst, i, len(poses), 150)
            
            poses_dst.append(bg)

        # add the images together vertically
        total = vertical_concat_multi(poses_dst)

        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        total.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'poses.png')   
    
    

    def has_custom_poses(self, user_id, place):
        return os.path.exists(self.get_pose_location(user_id, place))



    def get_pose_location(self, user_id, place):
        return f"{BASE_LOCATION}{str(user_id)}/Pose{place}.png"



    def has_prerender_of_poses(self, user_id):
        return os.path.exists(f"{BASE_LOCATION}{str(user_id)}/AllPoses.png")
    


    def add_numbering_to_poses(self, dst, start_number, number_of_poses, padding):
        # add poses to bg image
        bg = Image.new('RGB', (dst.width, dst.height + 400), (44, 45, 47))
        bg.paste(dst, (0,0))

        draw = ImageDraw.Draw(bg)
        font = ImageFont.truetype(f"{BASE_LOCATION}../fonts/contb.ttf", size=200)

        offset_per_pose = 450 + padding + 450
        y_paste = int(dst.height + (bg.height - dst.height) // 2)

        # add numbering of poses
        for i, number in enumerate(range(start_number, start_number+number_of_poses)):
            draw.text(
                (450 + offset_per_pose*i, y_paste),
                text=str(number+1),
                align='center', font=font, anchor='mm', fill=(255, 104, 1)
            )

        return bg
    


class PodiumBuilder:
    def __init__(self, bot) -> None:
        self.bot = bot

        self.character_builder = CharacterBuilder(bot)



    def user_has_podium(self, user_id, place=1, shiny=False):
        if not shiny:
            return os.path.exists(f"{BASE_LOCATION}{str(user_id)}/Podium{place}.png")
    
        return os.path.exists(f"{BASE_LOCATION}{str(user_id)}/ShinyPodium{place}.png")



    async def get_podium_image(self, user_id, place, always_shiny = False):

        # get location of the podium
        if self.user_has_podium(user_id, place):
            location = f"{BASE_LOCATION}{str(user_id)}/Podium{place}.png"
        else:
            location = f"{BASE_LOCATION}default/Podium{place}.png"


        # check if podium can be shiny and if it should be
        if always_shiny and self.user_has_podium(user_id, place, shiny=True):
            location = f"{BASE_LOCATION}{str(user_id)}/ShinyPodium{place}.png"
        
        # load the selected image
        image = Image.open(location)
        
        return image
    

    
    async def get_all_podiums_image(self, user_ids, return_file=True, padding=200, color=(44, 45, 47), add_characters=True):
        # create normalised images for every given podium
        if len(user_ids) == 1:
            order = [1]
        elif len(user_ids) == 2:
            order = [2, 1]
        else:
            order = [2, 1, 3]
        
        # 1 in 12 chance that the podiums are shiny (if possible)
        always_shiny = random.randint(1, 12) == 2

        podiums = []
        # for every available user (top 3)
        for i, id in enumerate(user_ids):
            # get podium
            podium_image = await self.get_podium_image(id, order[i], always_shiny)

            if add_characters: 

                # get active pose and pick 1 at random
                poses = await db_manager.get_poses(str(id), i+1)
                if poses is not None:
                    pose = random.choice([int(pose) for pose in poses[0]])
                else:
                    pose = random.randint(1, self.character_builder.get_amount_of_poses(str(id)))

                # add character
                podium_image = await self.character_builder.add_character_to_podium(podium_image, str(id), pose, order[i])

            podiums.append(podium_image)


        # paste podiums on correct location
        if len(podiums) == 3:
            dst = get_concat(podiums[1], podiums[0], podiums[2])
        else:
            dst = get_concat_h_multi_blank(podiums, padding, color)

        # return as image if necessary
        if not return_file:
            return dst
        
        # create buffer
        buffer = io.BytesIO()

        # save PNG in buffer
        dst.save(buffer, format='PNG')    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'podium.png')   



### HELPER FUNCTIONS ###

def vertical_concat_multi(images):
    _im = images.pop(0)
    for im in images:
        _im = vertical_concat(_im, im)
    return _im  



def vertical_concat(im1, im2):
    width1, height1 = im1.size
    width2, height2 = im2.size

    # Create a new image with the combined width and the height of the tallest image
    new_width = max(width1, width2)
    new_height = height1 + height2
    new_image = Image.new("RGB", (new_width, new_height), (44, 45, 47))

    # Paste the two images onto the new image
    new_image.paste(im1, (0, 0))
    # center second image
    remaining_width = new_width - width2
    new_image.paste(im2, (remaining_width//2, height1))

    return new_image



# concat multiple images with overlap (only if all 3 podiums present)
def get_concat(main_image, left_image, right_image):
    # calculate padding
    padding = min(main_image.width//3, 220)
    
    # create bg image with correct dimensions
    dst = Image.new(
        'RGBA', 
        (min(left_image.width, right_image.width) *3 + padding*2,
        max(left_image.height, main_image.height, right_image.height))
    )

    # paste the podiums onto the bg
    paste_width = (dst.width - main_image.width)//2
    dst.paste(main_image, (paste_width, 0), main_image)
    dst.paste(left_image, (0, dst.height - left_image.height), left_image)
    dst.paste(right_image, (dst.width - right_image.width, dst.height - left_image.height), right_image)
    
    return dst



# concat multiple images
def get_concat_h_multi_blank(im_list, padding, color=(44, 45, 47)):
    _im = im_list.pop(0)
    for im in im_list:
        _im = get_concat_h_blank(_im, im, padding, color)
    return _im



# concat 2 images
def get_concat_h_blank(im1, im2, padding, color=(44, 45, 47)):
    dst = Image.new('RGBA', (im1.width + im2.width + padding, im1.height), color)
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width + padding, 0))
    return dst



def remove_transparency(im, color=(44, 45, 47)):
    im = im.convert("RGBA")
    new_image = Image.new("RGBA", im.size, color)
    new_image.paste(im, mask=im)

    return new_image.convert("RGB")



def resize_image(im, width, max_height=1000, color=(44, 45, 47)):
    wpercent = (width / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(wpercent)))

    # calculated height exceedes max height
    if hsize > max_height:
        hsize = max_height
        hpercent = (hsize / float(im.size[1]))
        width = int((float(im.size[0]) * float(hpercent)))

    return im.resize((width, hsize), Image.Resampling.LANCZOS)



# get number in human format
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])