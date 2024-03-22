from PIL import Image, ImageDraw, ImageFont, ImageSequence
import discord
import io
import os
import requests
import random
import csv
from helpers import db_manager
from concurrent.futures import ThreadPoolExecutor
from itertools import zip_longest

# BASE_LOCATION = 'C:/Users/Silas/OneDrive/Documenten/GitHub/WhereContextBot3/media/images/'
BASE_LOCATION = 'media/images/'

POOL = ThreadPoolExecutor()

class LeaderboardBuilder:
    def __init__(self, bot) -> None:
        self.bot = bot

        self.podium_builder = PodiumBuilder(bot)


    async def async_set_leaderboard_images(self, loop, top_message, bottom_message, leaderboard, command):
                 
        top_file = await loop.run_in_executor(POOL, self.get_top_leaderboard, leaderboard, command)
        bottom_file = await loop.run_in_executor(POOL, self.get_bottom_leaderboard, leaderboard)

        await top_message.edit(embed=None, attachments=[top_file])
        await bottom_message.edit(embed=None, attachments=[bottom_file])



    def get_top_leaderboard(self, leaderboard, command):
        #  load background
        bg = Image.open(f"{BASE_LOCATION}leaderboard/LeaderboardTop.png")
        bg = bg.convert('RGBA')

        # load fonts
        fontb = ImageFont.truetype(f"{BASE_LOCATION}../fonts/contb.ttf", size=150)

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
        podium_image = self.podium_builder.get_all_podiums_image([pod[0] for pod in podiums], False, color=(62,62,62), add_characters=True)
        podium_image = resize_image(podium_image, 2000, 1800)
        remaining_width = bg.width - podium_image.width

        frames = []
        for frame in ImageSequence.Iterator(podium_image):
            
            output = bg.copy()

            output.paste(frame, (remaining_width//2, output.height - frame.height - 150), frame.convert("LA"))

            # create object for drawing
            draw = ImageDraw.Draw(output)

            # draw title
            draw.text(
                (1330, 245),
                text=command,
                align='center', font=fontb, anchor='mm', fill=(255, 104, 1)
            )
            del draw

            frames.append(output)


        # create buffer
        buffer = io.BytesIO()

        # save GIF in buffer
        frames[0].save(buffer, format='gif', save_all=True, append_images=frames[1:], loop=0, disposal=2) 

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'leaderboardtop.gif')
    


    def get_bottom_leaderboard(self, leaderboard):
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
            user = self.bot.get_user(int(user_id))
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

        # save GIF in buffer
        bg.save(buffer, format='png')    

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
    


    def get_extra_pose_data(self, user_id):

        amount_of_poses = self.get_amount_of_poses(user_id)

        # check if extra data exists
        if not os.path.exists(f"{BASE_LOCATION}{str(user_id)}/PoseData.csv"):
            return ([None] * amount_of_poses, None)
        
        with open(f"{BASE_LOCATION}{str(user_id)}/PoseData.csv") as f:
            reader = csv.DictReader(f, delimiter=",")
            data = list(reader)[0]
            data_list = []
            data_badge_list = []

            for i in range(1, amount_of_poses+1):
                # make pose offset correct format
                if data[str(i)] == "None":
                    data_list.append(None)
                    data_badge_list.append([True] *3)

                else:
                    offsets = data[str(i)].split(";")
                    data_list.append([
                        (int(offsets[0]), int(offsets[1])),
                        (int(offsets[3]), int(offsets[4])),
                        (int(offsets[6]), int(offsets[7])),
                    ])
                    data_badge_list.append([
                        eval(offsets[2]),
                        eval(offsets[5]),
                        eval(offsets[8])
                    ])

        return (data_list, data_badge_list)



    def add_character_to_podium(self, podium_image, user_id, poseNumber, place, podium_user_id):
        # get object that contains info about the arts done
        defined_art_user = self.get_extra_pose_data(user_id)
        defined_art_podium = self.get_extra_data(podium_user_id)

        # get location of the character
        if self.has_custom_poses(user_id, poseNumber):
            custom_character_location = self.get_pose_location(user_id, poseNumber)
        else:
            custom_character_location = f"{BASE_LOCATION}default/Pose{poseNumber}.png"

        # load the character image
        character_image = Image.open(custom_character_location)
        
        # resize it
        character_image = resize_image(character_image, 700)

        # create empty bg to add podium and character to
        background = Image.new('RGBA', (podium_image.width, podium_image.height + character_image.height))
        
        offset = defined_art_podium.get("poseOffset", [(0, 110), (0, 200), (0, 370)])[place-1]
        # different offset for specific pose
        if defined_art_user[0][poseNumber-1] is not None:
            offset = defined_art_user[0][poseNumber-1][place-1]

        paste_coords = defined_art_podium.get(
            "badgePasteCoords", 
            [(255, 1050), (255, 1130), (255, 1320)]
        )

        badge_image = Image.open(f"{BASE_LOCATION}badges/Badge{place}.png")

        frames = []
        for frame in ImageSequence.Iterator(character_image):
            
            output = background.copy()
            
            # paste podium
            output.paste(podium_image, (0, character_image.height), mask=podium_image) 
            
            # paste character
            output.paste(
                frame,
                ((background.width - frame.width)//2 + offset[0], offset[1]), 
                mask=frame.convert("LA")
            )

            # paste badge to fix 3d realness of character standing on podium
            output.paste(badge_image, paste_coords[place-1], mask=badge_image)        

            frames.append(output)

        # create buffer
        buffer = io.BytesIO()

        # save GIF in buffer
        frames[0].save(buffer, format='gif', save_all=True, append_images=frames[1:], loop=0, disposal=2)

        return Image.open(buffer)
    


    def get_amount_of_poses(self, user_id):
        # user does not have custom pose, so default 5 poses
        if not self.has_custom_poses(user_id, 1):
            return 5
        
        i = 2 # start at 2 since we already checked pose 1
        while self.has_custom_poses(user_id, i):
            i+=1

        return i-1
    


    async def async_set_all_poses_image(self, loop, user_id, message):
        poses_image = await loop.run_in_executor(POOL, self.get_all_poses_image, user_id)

        await message.edit(attachments=[poses_image])            



    def get_all_poses_image(self, user_id):

        # prerenderd of default all poses
        if not self.has_custom_poses(user_id):
            return discord.File(
                f"{BASE_LOCATION}default/AllPoses.gif", # TODO make this file
                'poses.png'
            ) 
        
        # prerendered of custom all poses
        if self.has_prerender_of_poses(user_id):
            return discord.File(
                f"{BASE_LOCATION}{str(user_id)}/AllPoses.gif",
                "poses.gif"
            )
        
        # not prerendered, create it
        poses = [
            Image.open(self.get_pose_location(user_id, i+1))
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

            poses_dst.append(
                self.get_pose_concat(poses_to_build, 150, i+1)
            )

            i += chunksize


        # leftover poses
        if len(poses) > 0:
            poses_dst.append(
                self.get_pose_concat(poses_to_build, 150, 1)
            )

        # add the images together vertically
        total = vertical_concat_multi(poses_dst)

        # create buffer
        buffer = io.BytesIO()

        # save GIF in buffer
        total.save(buffer, format='gif', save_all=True, loop=0, disposal=2)    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        # return total
        return discord.File(buffer, 'poses.gif')   
    


    def get_pose_concat(self, poses, padding, start_number, color=(44, 45, 47)):
        new_width = sum([im.width for im in poses]) + padding*(len(poses) - 1)
        background = Image.new('RGBA', (new_width, poses[0].height + 400), color)
        font = ImageFont.truetype(f"{BASE_LOCATION}../fonts/contb.ttf", size=200)
        text_y_paste = background.height - 200

        total_frame_count = max(*[gif.n_frames for gif in poses])
        frames = []
        for i in range(total_frame_count):
            
            output = background.copy()
            current_x_point = 0

            for number, pose in enumerate(poses):
                pose.seek(i)
                frame = pose.copy()

                output.paste(
                    frame, 
                    (current_x_point, 0), 
                    mask=frame.convert("LA")
                )

                text_x_paste = current_x_point - 50 + pose.width // 2
                draw = ImageDraw.Draw(output)
                draw.text(
                    (text_x_paste, text_y_paste),
                    text=str(number+start_number),
                    align='center', font=font, anchor='mm', fill=(255, 104, 1)
                )
                del draw

                current_x_point += pose.width + padding

            frames.append(output)


        # create buffer
        buffer = io.BytesIO()

        # save gif in buffer
        frames[0].save(buffer, format='gif', save_all=True, append_images=frames[1:], loop=0, disposal=2)

        return Image.open(buffer)


        
    def has_custom_poses(self, user_id, pose=1):
        return os.path.exists(f"{BASE_LOCATION}{str(user_id)}/Pose{pose}.gif") or os.path.exists(f"{BASE_LOCATION}{str(user_id)}/Pose{pose}.png")



    def get_pose_location(self, user_id, pose):
        if os.path.exists(f"{BASE_LOCATION}{str(user_id)}/Pose{pose}.gif"):
            return f"{BASE_LOCATION}{str(user_id)}/Pose{pose}.gif"

        return f"{BASE_LOCATION}{str(user_id)}/Pose{pose}.png"



    def has_prerender_of_poses(self, user_id):
        return os.path.exists(f"{BASE_LOCATION}{str(user_id)}/AllPoses.gif")
     


class PodiumBuilder:
    def __init__(self, bot) -> None:
        self.bot = bot

        self.character_builder = CharacterBuilder(bot)


    def user_has_podium(self, user_id, place=1, shiny=False):
        if not shiny:
            return os.path.exists(f"{BASE_LOCATION}{str(user_id)}/Podium{place}.png")
    
        return os.path.exists(f"{BASE_LOCATION}{str(user_id)}/ShinyPodium{place}.png")


    def get_podium_image(self, user_id, place, always_shiny = False):

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
    

    def get_all_podiums_image(self, user_ids, return_file=True, padding=200, color=(44, 45, 47), add_characters=True, characters=None):
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
            podium_image = self.get_podium_image(id, order[i], always_shiny)

            if add_characters: 
                
                if characters is not None:
                    id_char = characters[i] if characters[i] is not None else id
                else:
                    # if characters not defined, take same id as from podium
                    id_char = id

                # get active pose and pick 1 at random
                poses = db_manager.get_poses(str(id_char), order[i]) # order[i] was i+1
                if poses is not None:
                    pose = random.choice([int(pose) for pose in poses[0]])
                else:
                    pose = random.randint(1, self.character_builder.get_amount_of_poses(str(id_char)))

                # add character
                podium_image = self.character_builder.add_character_to_podium(podium_image, str(id_char), pose, order[i], str(id))

            podiums.append(podium_image)


        # paste podiums on correct location
        if len(podiums) == 3:
            final_image = get_concat(podiums[1], podiums[0], podiums[2])
        else:
            final_image = get_concat_h_multi_blank(podiums, padding, color)
            
        # return as image if necessary
        if not return_file:
            return final_image
        
        # create buffer
        buffer = io.BytesIO()

        # save GIF in buffer
        final_image.save(buffer, format='gif', save_all=True, loop=0, disposal=2, optimize=False)    

        # move to beginning of buffer so `send()` it will read from beginning
        buffer.seek(0)

        return discord.File(buffer, 'podium.gif')  



    async def async_set_all_podiums_image(self, loop, message, embed, user_id, user_ids, padding, add_characters):
                 
        # show podiums if user has one
        if self.user_has_podium(user_id):
            podiums_image = await loop.run_in_executor(POOL, self.get_all_podiums_image, user_ids, True, padding, (44, 45, 47), add_characters)
            embed.set_image(url="attachment://podium.gif")

            await message.edit(embed=embed, attachments=[podiums_image])


    async def async_set_all_podiums_image_file(self, loop, message, user_ids, characters):
                
        # show podiums if user has one
        podiums_image = await loop.run_in_executor(POOL, self.get_all_podiums_image, user_ids, True, 200, (44, 45, 47), True, characters)
        await message.edit(embed=None, attachments=[podiums_image]) 



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
    background = Image.new("RGB", (new_width, new_height), (44, 45, 47))

    total_frame_count = max(im1.n_frames, im2.n_frames)
    frames = []
    for i in range(total_frame_count):
        
        output = background.copy()

        im1.seek(i)
        frame1 = im1.copy()

        # Paste the two images onto the new image
        output.paste(frame1, (0, 0), mask=frame1.convert("LA"))

        # center second image
        im2.seek(i)
        frame2 = im2.copy()
        remaining_width = new_width - width2
        output.paste(frame2, (remaining_width//2, height1), mask=frame2.convert("LA"))

        frames.append(output)


    # create buffer
    buffer = io.BytesIO()

    # save GIF in buffer
    frames[0].save(buffer, format='gif', save_all=True, append_images=frames[1:], loop=0, disposal=2)

    return Image.open(buffer)


# concat multiple images with overlap (only if all 3 podiums present)
def get_concat(main_image, left_image, right_image):
    # calculate padding
    padding = min(main_image.width//3, 220)
    
    # create bg image with correct dimensions
    background = Image.new(
        'RGBA', 
        (min(left_image.width, right_image.width) *3 + padding*2,
        max(left_image.height, main_image.height, right_image.height))
    )

    paste_width = (background.width - main_image.width)//2


    main_frames = [frame.copy() for frame in ImageSequence.Iterator(main_image)]
    left_frames = [frame.copy() for frame in ImageSequence.Iterator(left_image)]
    right_frames = [frame.copy() for frame in ImageSequence.Iterator(right_image)]

    frames = []
    for main_frame, left_frame, right_frame in zip_longest(main_frames, left_frames, right_frames):
        
        output = background.copy()

        # check if each frame has frames left
        if main_frame is None:
            main_image.seek(0)
            main_frame = main_image.copy()

        if left_frame is None:
            left_image.seek(0)
            left_frame = left_image.copy()

        if right_frame is None:
            right_image.seek(0)
            right_frame = right_image.copy()

        output.paste(main_frame, (paste_width, 0), mask=main_frame.convert("LA"))
        output.paste(left_frame, (0, output.height - left_frame.height), mask=left_frame.convert("LA"))
        output.paste(right_frame, (output.width - right_frame.width, output.height - left_frame.height), mask=right_frame.convert("LA"))

        frames.append(output)


    # create buffer
    buffer = io.BytesIO()

    # save GIF in buffer
    frames[0].save(buffer, format='gif', save_all=True, append_images=frames[1:], loop=0, disposal=2, optimize=False)

    return Image.open(buffer) 



# concat multiple images
def get_concat_h_multi_blank(im_list, padding, color=(44, 45, 47)):
    _im = im_list.pop(0)
    for im in im_list:
        _im = get_concat_h_blank(_im, im, padding, color)
    return _im



# concat 2 images
def get_concat_h_blank(im1, im2, padding, color=(44, 45, 47)):

    background = Image.new('RGBA', (im1.width + im2.width + padding, im1.height), color)
    
    total_frame_count = max(im1.n_frames, im2.n_frames)
    frames = []
    for i in range(total_frame_count):
        
        output = background.copy()

        im1.seek(i)
        frame1 = im1.copy()

        # Paste the two images onto the new image
        output.paste(frame1, (0, 0), mask=frame1.convert("LA"))

        im2.seek(i)
        frame2 = im2.copy()
        output.paste(frame2, (im1.width + padding, 0), mask=frame2.convert("LA"))

        frames.append(output)


    # create buffer
    buffer = io.BytesIO()

    # save GIF in buffer
    frames[0].save(buffer, format='gif', save_all=True, append_images=frames[1:], loop=0, disposal=2, optimize=False)

    return Image.open(buffer)



def resize_image(im, width, max_height=1000, color=(44, 45, 47)):
    wpercent = (width / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(wpercent)))

    # calculated height exceedes max height
    if hsize > max_height:
        hsize = max_height
        hpercent = (hsize / float(im.size[1]))
        width = int((float(im.size[0]) * float(hpercent)))

    frames = []
    for frame in ImageSequence.Iterator(im):

        frame_resized = frame.resize((width, hsize), Image.Resampling.LANCZOS)
        frames.append(frame_resized)

    # create buffer
    buffer = io.BytesIO()

    # save GIF in buffer
    frames[0].save(buffer, format='gif', save_all=True, append_images=frames[1:], loop=0, disposal=2)

    return Image.open(buffer)


# get number in human format
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])