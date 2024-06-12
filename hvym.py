import os
import click
import subprocess
import shutil
import json
import subprocess
import threading
import concurrent.futures
from subprocess import run, Popen, PIPE
from platformdirs import *
from pygltflib import GLTF2
from dataclasses import dataclass, asdict, field
from dataclasses_json import dataclass_json
from jinja2 import Environment, FileSystemLoader
from gifanimus import GifAnimation
from pathlib import Path
import numbers
import hashlib
import dload
import re
import time

ABOUT = """
Command Line Interface for Heavymeta Standard NFT Data
By: Fibo Metavinci
All Rights Reserved
"""
VERSION = "0.01"

FILE_PATH = Path(__file__).parent

TEMPLATE_MODEL_VIEWER_INDEX = 'model_viewer_html_template.txt'
TEMPLATE_MODEL_VIEWER_JS = 'model_viewer_js_template.txt'
TEMPLATE_MODEL_MINTER_INDEX = 'model_minter_frontend_index_template.txt'
TEMPLATE_MODEL_MINTER_JS = 'model_minter_frontend_js_template.txt'
TEMPLATE_MODEL_MINTER_MAIN = 'model_minter_backend_main_template.txt'
TEMPLATE_MODEL_MINTER_TYPES = 'model_minter_backend_types_template.txt'

MODEL_MINTER_REPO = 'https://github.com/inviti8/hvym_minter_template.git'
MODEL_MINTER_ZIP = 'https://github.com/inviti8/hvym_minter_template/archive/refs/heads/master.zip'
MINTER_TEMPLATE = 'hvym_minter_template-master'
MODEL_TEMPLATE = 'model'
LOADING_IMG = os.path.join(FILE_PATH, 'images', 'loading.gif')
BUILDING_IMG = os.path.join(FILE_PATH, 'images', 'building.gif')


#Material Data classes
@dataclass_json
@dataclass
class base_data_class:
      @property
      def dictionary(self):
            return asdict(self)

      @property
      def json(self):
            return json.dumps(self.dictionary)


@dataclass_json
@dataclass
class collection_data_class(base_data_class):
      '''
      Base data class for hvym collection properties
      :param collectionName: Name of collection
      :type collectionName:  (str)
      :param collectionType: Type of collection based on constants: ('multi', 'single')
      :type collectionType:  (str)
      :param valProps: Value properties dictionary
      :type valProps:  (dict)
      :param callProps: Method call properties dictionary
      :type callProps:  (dict)
      :param meshProps: Mesh Properties dictionary
      :type meshProps:  (dict)
      :param meshSets: Mesh sets dictionary
      :type meshSets:  (dict)
      :param morphSets: Morph sets dictionary
      :type morphSets:  (dict)
      :param animProps: Mesh sets dictionary
      :type animProps:  (dict)
      :param matProps: Material properties dictionary
      :type matProps:  (dict)
      :param materialSets: Mesh sets dictionary
      :type materialSets:  (dict)
      :param menuData: Menu data dictionary
      :type menuData:  (dict)
      :param propLabelData: Property labels dictionary
      :type propLabelData:  (dict)
      :param nodes: List of all nodes in the collection
      :type nodes:  (dict)
      :param actionProps: List of all nodes in the collection
      :type actionProps:  (dict)
      '''
      collectionName: str
      collectionType: str
      valProps: dict
      callProps: dict
      meshProps: dict
      meshSets: dict
      morphSets: dict
      animProps: dict
      matProps: dict
      materialSets: dict
      menuData: dict
      propLabelData: dict
      nodes: dict
      actionProps: dict


@dataclass_json
@dataclass
class contract_data_class(base_data_class):
      '''
      Base data class for contract data
      :param mintable: Whether or not this nft is mintable
      :type mintable:  (bool)
      :param nftType: Type of nft based on constants: ('HVYC', 'HVYI', 'HVYA', 'HVYW', 'HVYO', 'HVYG', 'HVYAU')
      :type nftType:  (str)
      :param nftChain: Block chain based on constants: ('ICP', 'EVM')
      :type nftChain:  (str)
      :param nftPrice: Price of NFT
      :type nftPrice  (int)
      :param nftPrice: Price of NFT
      :type nftPrice  (int)
      :param premNftPrice: Premium price of NFT
      :type premNftPrice  (int)
      :param maxSupply: Maximum supply of NFT
      :type maxSupply  (int)
      :param minterType: Type of minter based on constants: ('payable', 'onlyOwner')
      :type minterType  (str)
      :param minterName: Name of minter
      :type minterName  (str)
      :param minterDesc: Description of minter
      :type minterDesc  (str)
      :param minterImage: Path to image file for NFT
      :type minterImage  (str)
      :param minterVersion: Type of minter based on constants: ('payable', 'onlyOwner')
      :type minterVersion  (float)
      '''
      mintable: bool
      nftType: str
      nftChain: str
      nftPrice: float
      premNftPrice: float
      maxSupply: int
      minterType: str
      minterName: str
      minterDesc: str
      minterImage: str
      minterVersion: float


@dataclass_json
@dataclass
class menu_data_class(base_data_class):
      '''
      Base data class for hvym menu properties
      :param name: Widget type to use
      :type name:  (str)
      :param primary_color: Primary color of menu
      :type primary_color:  (str)
      :param secondary_color: Secondary color of menu
      :type secondary_color:  (str)
      :param text_color: text color of menu
      :type text_color:  (str)
      :param alignment: Alignment of menu relative to transform based on string constants: ('CENTER', 'LEFT', 'RIGHT')
      :type alignment:  (str)
      '''
      name: str
      primary_color: str
      secondary_color: str
      text_color: str
      alignment: str


@dataclass_json
@dataclass
class action_data_class(base_data_class):
      '''
      Base data class for hvym action properties
      :param anim_type: Widget type to use
      :type anim_type:  (str)
      :param set: Mesh ref list
      :type set:  (list)
      :param interaction: Interaction type to use
      :type interaction:  (str)
      :param sequence: How animation is sequenced
      :type sequence:  (str)
      :param additive: Set the type of animation blending
      :type additive:  (bool)
      '''
      anim_type: str
      set: list
      interaction: str
      sequence: str
      additive: bool

@dataclass_json
@dataclass
class action_mesh_data_class(action_data_class):
      '''
      Base data class for hvym action properties
      :param model_ref: Model reference properties
      :type model_ref:  (object)
      '''
      model_ref: dict


@dataclass_json
@dataclass
class property_label_data_class(base_data_class):
      '''
      Base data class for widget data
      :param value_prop_label: Value Property Label
      :type value_prop_label:  (str)
      :param call_prop_label: Value Property Label
      :type call_prop_label:  (str)
      :param mesh_prop_label: Mesh Propertty Label
      :type mesh_prop_label:  (str)
      :param mat_prop_label: Material Property Label
      :type mat_prop_label:  (str)
      :param anim_prop_label: Animation Property Label
      :type anim_prop_label:  (str)
      :param mesh_set_label: Mesh Set Label
      :type mesh_set_label:  (str)
      :param morph_set_label: Morph Set Label
      :type morph_set_label:  (str)
      :param mat_set_label: MaterialSet Label
      :type mat_set_label:  (str)
      '''
      value_prop_label: str
      call_prop_label: str
      mesh_prop_label: str
      mat_prop_label: str
      anim_prop_label: str
      mesh_set_label: str
      morph_set_label: str
      mat_set_label: str


@dataclass_json
@dataclass
class widget_data_class(base_data_class):
      '''
      Base data class for widget data
      :param widget_type: Widget type to use
      :type widget_type:  (str)
      :param show: if false, hide widget
      :type show:  (bool)
      '''
      widget_type: str
      show: bool


@dataclass_json
@dataclass
class slider_data_class(widget_data_class):
      '''
      Base data class for slider data
      :param prop_slider_type: Slider type to use
      :type prop_slider_type:  (int)
      :param prop_action_type: Action type to use
      :type prop_action_type:  (int)
      '''
      prop_slider_type: str
      prop_action_type: str


@dataclass_json
@dataclass
class single_int_data_class(base_data_class):
      '''
      Creates data object for singular int data value property
      :param name: Element name
      :type name:  (str)
      :param default: Default integer value
      :type default:  (int)
      :param min: Minimum integer value
      :type min:  (int)
      :param max: Maximum integer value
      :type max:  (int)
      '''
      name: str
      default: int
      min: int
      max: int

@dataclass_json
@dataclass
class call_data_class(base_data_class):
      '''
      Creates data object for a method call reference
      :param name: Method name
      :type name:  (str)
      :param call_param: Mesh visiblility
      :type call_param:  (str)
      '''
      name: str
      call_param: str


@dataclass_json
@dataclass
class int_data_class(slider_data_class):
      '''
      Creates data object for int data value property
      :param default: Default integer value
      :type default:  (int)
      :param min: Minimum integer value
      :type min:  (int)
      :param max: Maximum integer value
      :type max:  (int)
      :param immutable: If immutable, property cannot be edited after minting.
      :type immutable:  (bool)
      '''
      default: int
      min: int
      max: int
      immutable: bool


@dataclass_json
@dataclass
class cremental_int_data_class(int_data_class):
      '''
      Creates data object for incremental and decremental data value property
      :param amount: The amount to increment or decrement
      :type amount:  (int)
      '''
      amount: int


@dataclass_json
@dataclass
class single_float_data_class(base_data_class):
      '''
      Creates data object for singular float data value property
      :param name: Element name
      :type name:  (str)
      :param default: Default integer value
      :type default:  (float)
      :param min: Minimum integer value
      :type min:  (float)
      :param max: Maximum integer value
      :type max:  (float)
      '''
      name: str
      default: float
      min: float
      max: float
      

@dataclass_json
@dataclass
class float_data_class(slider_data_class):
      '''
      Creates data object for float data value property
      :param default: Default integer value
      :type default:  (float)
      :param min: Minimum integer value
      :type min:  (float)
      :param max: Maximum integer value
      :type max:  (float)
      :param immutable: If immutable, property cannot be edited after minting.
      :type immutable:  (bool)
      '''
      default: float
      min: float
      max: float
      immutable: bool
      

@dataclass_json
@dataclass
class cremental_float_data_class(float_data_class):
      '''
      Creates data object for incremental and decremental data value property
      :param amount: The amount to increment or decrement
      :type amount:  (float)
      '''
      amount: float


@dataclass_json
@dataclass
class single_mesh_data_class(base_data_class):
      '''
      Creates data object for singular mesh reference
      :param name: Mesh name
      :type name:  (str)
      :param min: Mesh visiblility
      :type min:  (str)
      '''
      name: str
      visible: bool


@dataclass_json
@dataclass
class single_node_data_class(base_data_class):
      '''
      Creates data object for singular mesh reference
      :param name: Mesh name
      :type name:  (str)
      :param type: Mesh visiblility
      :type type:  (str)
      '''
      name: str
      type: str


@dataclass_json
@dataclass
class mesh_data_class(widget_data_class):
      '''
      Creates data object for a mesh reference
      :param name: Mesh name
      :type name:  (str)
      :param min: Mesh visiblility
      :type min:  (str)
      '''
      name: str
      visible: bool
      

@dataclass_json
@dataclass
class mesh_set_data_class(widget_data_class):
      '''
      Creates data object for a mesh set
      :param set: Mesh ref list
      :type set:  (list)
      :param min: Mesh visiblility
      :type min:  (str)
      '''
      set: list
      selected_index: int


@dataclass_json
@dataclass
class morph_set_data_class(widget_data_class):
      '''
      Creates data object for a morph set
      :param set: Mesh ref list
      :type set:  (list)
      :param selected_index: Selected index for the list
      :type selected_index:  (int)
      :param model_ref: Model reference properties
      :type model_ref:  (object)
      '''
      set: list
      selected_index: int
      model_ref: dict


@dataclass_json
@dataclass
class mat_set_data_class(widget_data_class):
      '''
      Creates data object for material set
      :param set: Material ref list
      :type set:  (list)
      :param mesh_set: Mesh ref list
      :type mesh_set:  (list)
      :param material_id: the material id that will materials will be assigned to
      :type material_id:  (int)
      :param selected_index: Selected index for the list
      :type selected_index:  (int)
      '''
      set: list
      mesh_set: list
      material_id: int
      selected_index: int


@dataclass_json
@dataclass
class anim_prop_data_class(widget_data_class):
      '''
      Creates data object for basic material reference
      :param name: Element name
      :type name:  (str)
      :param loop: Animation looping property based on string constants: ('NONE', 'LoopRepeat', 'LoopOnce', 'ClampToggle', 'Clamp', 'PingPong')
      :type loop:  (str)
      :param start: Start frame of animation
      :type start:  (int)
      :param end: End frame of animation
      :type end:  (int)
      :param blending: Animation blending based on string constant
      :type blending:  (str)
      :param weight: Amount animation affects element
      :type weight:  (float)
      :param play: If true, animation should play
      :type play:  (bool)
      :param model_ref: Model reference properties
      :type model_ref:  (object)
      '''
      name: str
      loop: str
      start: int
      end: int
      blending: str
      weight: float
      play: bool
      model_ref: dict


@dataclass_json
@dataclass
class mat_prop_data_class(widget_data_class):
      '''
      Creates data object for basic material reference
      :param name: Element name
      :type name:  (str)
      :param type: Material type property based on string constants: ('STANDARD', 'PBR', 'TOON')
      :type type:  (str)
      :param emissive: If true, material is emissive
      :type emissive:  (bool)
      :param reflective: If true, material is reflective
      :type reflective:  (bool)
      :param irridescent: If true, material is irridescent
      :type irridescent:  (bool)
      :param sheen: If true, material has sheen
      :type sheen:  (bool)
      :param mat_ref: Object representation of the mesh material
      :type mat_ref:  (object)
      :param save_data: Empty dictionary into which material save data goes
      :type save_data:  (object)
      '''
      name: str
      type: str
      emissive: bool
      reflective: bool
      irridescent: bool
      sheen: bool
      mat_ref: dict
      save_data: dict
      
      
@dataclass_json
@dataclass
class basic_material_class(base_data_class):
      '''
      Creates data object for basic material reference
      :param color: String identifier for color hex
      :type color:  (str)
      :param emissive: String identifier for color hex
      :type emissive:  (str)
      :param emissive_intensity: Float for emissive intensity
      :type emissive_intensity:  (float)
      '''
      color: str
      emissive: str = None
      emissive_intensity: float = None
    

@dataclass_json
@dataclass
class lambert_material_class(base_data_class):
       '''
      Creates data object for lambert material reference
      :param color: String identifier for color hex
      :type color:  (str)
      :param emissive: String identifier for color hex
      :type emissive:  (str)
      :param emissive_intensity: Float for emissive intensity
      :type emissive_intensity:  (float)
      '''
       color: str
       emissive: str = None
       emissive_intensity: float = None
    

@dataclass_json
@dataclass
class phong_material_class(base_data_class):
      '''
      Creates data object for phong material reference
      :param color: String identifier for color hex
      :type color:  (str)
      :param specular: String identifier for color hex
      :type specular:  (str)
      :param shininess: float value for shine
      :type shininess:  (float)
      :param emissive: String identifier for color hex
      :type emissive:  (str)
      :param emissive_intensity: Float for emissive intensity
      :type emissive_intensity:  (float)
      '''
      color: str
      specular: str
      shininess: float
      emissive: str = None
      emissive_intensity: float = None


@dataclass_json
@dataclass
class standard_material_class(base_data_class):
       '''
      Creates data object for standard material reference
      :param color: String identifier for color hex
      :type color:  (str)
      :param roughness: float for roughness
      :type roughness:  (float)
      :param metalness: float value for metalness
      :type metalness:  (float)
      :param emissive: String identifier for color hex
      :type emissive:  (str)
      :param emissive_intensity: Float for emissive intensity
      :type emissive_intensity:  (float)
      '''
       color: str
       roughness: float
       metalness: float
       emissive: str = None
       emissive_intensity: float = None


@dataclass_json
@dataclass
class pbr_material_class(base_data_class):
      '''
      Creates data object for pbr material reference
      :param color: String identifier for color hex
      :type color:  (str)
      :param roughness: float for roughness
      :type roughness:  (float)
      :param metalness: float value for metalness
      :type metalness:  (float)
      :param iridescent: if true, material has irridescent property exposed
      :type iridescent:  (bool)
      :param sheen_color: Sheen color
      :type sheen_color:  (str)
      :param sheen_weight: float value for iridescence
      :type sheen_weight:  (float)
      :param emissive: String identifier for color hex
      :type emissive:  (str)
      :param emissive_intensity: Float for emissive intensity
      :type emissive_intensity:  (float)
      '''
      color: str
      roughness: float
      metalness: float
      iridescent: bool = None
      sheen_color: str = None
      sheen_weight: float = None
      emissive: str = None
      emissive_intensity: float = None

@dataclass_json
@dataclass
class interactable_data_class(base_data_class):
      '''
      Base data class for hvym interactables properties
      :param interaction_type: String for interaction type
      :type interaction_type:  (str)
      :param name: String for interaction name
      :type name:  (str)
      :param call: String for interaction call
      :type call:  (str)
      :param param_type: String for interaction type
      :type param_type:  (str)
      '''
      interaction_type: str
      name: str
      call: str
      param_type: str


@dataclass_json
@dataclass
class interactables_data_class(base_data_class):
      '''
      Base data class for hvym interactables properties
      :param elements: Mesh ref list
      :type elements:  (list)
      '''
      interactables: list
      

@dataclass_json
@dataclass      
class model_debug_data(base_data_class):
      '''
      Creates data object to be used in jinja text renderer for model debug templates.
      :param model: String identifier for model file name including extension
      :type model:  (str)
      :param model_name String identifier for model file name without extension.
      :type model_name:  (str)
      :param js_file_name: String identifier for js file name with extension.
      :type js_file_name:  (str)
      '''
      model: str
      model_name: str
      js_file_name: str
      
def _new_session(chain, name):
      home = os.path.expanduser("~").replace('\\', '/') if os.name == 'nt' else os.path.expanduser("~")

      app_dirs = PlatformDirs('heavymeta-cli', 'HeavyMeta')
      path = os.path.join(app_dirs.user_data_dir, f'{chain}', name)

      if not os.path.exists(path):
        os.makedirs(path)

      session_file = os.path.join(app_dirs.user_data_dir, f'{chain}_session.txt')
      with open(session_file, 'w') as f:
        f.write(path)

      return path
        

def _get_session(chain):
      """Get the active project session path."""
      dirs = PlatformDirs('heavymeta-cli', 'HeavyMeta')
      session_file = os.path.join(dirs.user_data_dir, f"{chain}_session.txt")
      path = 'NOT SET!!'
      if not os.path.exists(session_file):
        click.echo(f"No {chain} session available create a new {chain}  project with '{chain} -project $project_name' ")
        return

      if os.path.exists(session_file):
        with open(session_file, 'r') as f:
            path = f.read().strip()

      return path


def _run_command(cmd):
      process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
      output, error = process.communicate()

      if process.returncode != 0:  
        print("Command failed with error:", error.decode('utf-8'))
      else:
        print(output.decode('utf-8'))

def _run_futures_cmds(path, cmds, procImg=LOADING_IMG):
      loading = GifAnimation(procImg, 1000, True, '', True)
      loading.Play()
      with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(run, cmd, shell=True, cwd=path): cmd for cmd in cmds}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=5) 
                #print( result.stdout)
                
            except Exception as e:  
                print("Command failed with error:", str(e))
                
      loading.Stop()
                

def _futures(chain, folders, commands, procImg=LOADING_IMG):
      session = _get_session(chain)
      path = os.path.join(*folders)
      asset_path = os.path.join(session, path)

      _run_futures_cmds(asset_path, commands, procImg)
    

def _subprocess_output(command, path, procImg=LOADING_IMG):
      loading = GifAnimation(procImg, 1000, True, '', True)
      loading.Play()
      try:
        output = subprocess.check_output(command, cwd=path, shell=True, stderr=subprocess.STDOUT)
        print(_extract_urls(output.decode('utf-8')))
        return output.decode('utf-8')
      except Exception as e:
        print("Command failed with error:", str(e))
      loading.Stop()
        

def _subprocess(chain, folders, command, procImg=LOADING_IMG):
      session = _get_session(chain)
      path = os.path.join(*folders)
      asset_path = os.path.join(session, path)

      return _subprocess_output(command, asset_path, procImg)

def _call(cmd):
      output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
      return output.stdout.encode('utf-8')

def _create_hex(value):
      sha256_hash = hashlib.sha256()
      sha256_hash.update(value)
      return sha256_hash.hexdigest()


def _icp_set_network(name, port):
      """Set the ICP network."""
      config_dir = user_config_dir()  # Gets the path to the config directory.
      networks_config = os.path.join(config_dir, 'dfx', 'networks.json')

      if not os.path.exists(networks_config):  # If networks.json does not exist
        with open(networks_config, 'w') as file:
            json.dump({"local": {"replica": {"bind": f"localhost:{port}","subnet_type": "application"}}}, file)
            

def _set_hvym_network():
      """Set the ICP  Heavymeta network."""
      _icp_set_network('hvym', 1357)
    

def _extract_urls(output):
      urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[\\\\/])*', output)
      return urls

def _exposed_mat_fields(mat_type, reflective=False, iridescent=False, sheen=False, emissive=False):
      props = []
      if mat_type ==  'BASIC':
            props.append('color')
            
      elif mat_type ==  'PHONG':
            props.append('color')
            props.append('specular')
            props.append('shininess')
            
      elif mat_type ==  'STANDARD':
            props.append('color')
            props.append('roughness')
            props.append('metalness')
            
      elif mat_type ==  'PBR':
            props.append('color')
            props.append('roughness')
            props.append('metalness')
            if reflective:
                  props.append('ior')
                  props.append('reflectivity')

            if iridescent:
                  props.append('iridescence')
                  props.append('iridescenceIOR')

            if sheen:
                  props.append('sheen')
                  props.append('sheenRoughness')
                  props.append('sheenColor')

            props.append('clearcoat')
            props.append('clearcoatRoughness')
            props.append('specularColor')
            
      elif mat_type ==  'PBR':
            props.append('color')


      if emissive:
            props.append('emissive')
            props.append('emissiveIntensity')

      return props


def _mat_save_data(mat_ref, mat_type, reflective=False, iridescent=False, sheen=False, emissive=False):
      fields = _exposed_mat_fields(mat_type, reflective, iridescent, sheen, emissive)
      props = {}

      for field in fields:
            if field in mat_ref:
                  props[field] = mat_ref[field]
            else:
                  props[field] = ""

      return props


def _ic_create_model_repo(path):
      folder = 'dapp'
      project_name = 'model_view'
      #Create the Debug directories
      os.makedirs(os.path.join(path, folder, 'src'))
      #Create the Assets directories
      os.makedirs(os.path.join(path,  'Assets', 'src'))
        
      dfx_json = {
        "canisters": {
            f"{project_name}_nft_container": {
            "main": "src/Main.mo"
            }
        }
      }
        
      with open(os.path.join(path, folder, 'dfx.json'), 'w') as f:
        json.dump(dfx_json, f)
            
      # Create empty Main.mo and Types.mo files
        with open(os.path.join(path, folder, 'src', 'Main.mo'), 'w') as f:
              pass
        
      with open(os.path.join(path, folder,  'src',  'Types.mo'), 'w') as f:
            pass

      dfx_json = {
        f"{project_name}": {
            f"{project_name}_assets": {
            "source": [
                f"src/{project_name}/"
                ],
            "type": "assets"
            }
        },
        "output_env_file": ".env"
      }
        
      with open(os.path.join(path, 'Assets', 'dfx.json'), 'w') as f:
        json.dump(dfx_json, f)


def _ic_create_model_minter_repo(path):
     dload.save_unzip(MODEL_MINTER_ZIP, path)

def _ic_model_path():
      return os.path.join(_get_session('icp'), MODEL_TEMPLATE)
      
def _ic_minter_path():
      return os.path.join(_get_session('icp'), MINTER_TEMPLATE)

def _ic_minter_model_path():
      return os.path.join(_ic_minter_path(), 'src', 'proprium_minter_frontend', 'assets')
      

@click.group()
def cli():
      pass


@click.command('parse-blender-hvym-interactables')
@click.argument('obj_data', type=str)
def parse_blender_hvym_interactables(obj_data):
      """Return parsed interactables data structure from blender for heavymeta gltf extension"""
      objs = json.loads(obj_data)
      data = interactables_data_class([])
      for key in objs:
            obj = objs[key]
            
            if obj['hvym_mesh_interaction_type'] != 'none':
                  d = interactable_data_class(obj['hvym_mesh_interaction_type'], obj['hvym_mesh_interaction_name'], obj['hvym_mesh_interaction_call'], obj['hvym_mesh_interaction_call_param']).dictionary
                  data.interactables.append(d)
      click.echo(data.json)


@click.command('parse-blender-hvym-collection')
@click.argument('collection_name', type=str)
@click.argument('collection_type', type=str)
@click.argument('collection_id', type=str)
@click.argument('collection_json', type=str)
@click.argument('menu_json', type=str)
@click.argument('nodes_json', type=str)
@click.argument('actions_json', type=str)
def parse_blender_hvym_collection(collection_name, collection_type, collection_id, collection_json, menu_json, nodes_json, actions_json):
      """Return parsed data structure from blender for heavymeta gltf extension"""
      col_data = json.loads(collection_json)
      menu_data = json.loads(menu_json)
      node_data = json.loads(nodes_json)
      action_data = json.loads(actions_json)
      val_props = {}
      call_props = {}
      mesh_props = {}
      mesh_sets = {}
      morph_sets = {}
      anim_props = {}
      mat_props = {}
      mat_sets = {}
      col_menu = {}
      prop_label_data = {}
      action_props = {}

      for i in col_data:
          if i.isdigit():
                obj = col_data[i]
                if obj['prop_action_type'] == 'Immutable' or obj['prop_action_type'] == 'Static':
                      int_props = int_data_class(obj['prop_slider_type'], obj['show'], obj['prop_slider_type'], obj['prop_action_type'], obj['int_default'], obj['int_min'], obj['int_max'], obj['prop_immutable']).dictionary
                else:
                      int_props = cremental_int_data_class(obj['prop_slider_type'], obj['show'], obj['prop_slider_type'], obj['prop_action_type'], obj['int_default'], obj['int_min'], obj['int_max'], obj['prop_immutable'], obj['int_amount']).dictionary
                
                if obj['prop_value_type'] == 'Float':
                      if obj['prop_action_type'] == 'Immutable' or obj['prop_action_type'] == 'Static':
                            int_props = int_data_class(obj['prop_slider_type'], obj['show'], obj['prop_slider_type'], obj['prop_action_type'], obj['float_default'], obj['float_min'], obj['float_max'], obj['prop_immutable']).dictionary
                      else:
                            int_props = cremental_float_data_class(obj['prop_slider_type'], obj['show'], obj['prop_slider_type'], obj['prop_action_type'], obj['float_default'], obj['float_min'], obj['float_max'], obj['prop_immutable'], obj['float_amount']).dictionary
                            
                      
                if obj['trait_type'] == 'property':
                      val_props[obj['type']] = int_props

                elif obj['trait_type'] == 'call':
                      call_props[obj['type']] = call_data_class(obj['type'], obj['call_param']).dictionary

                elif obj['trait_type']  == 'mesh':
                      if obj['model_ref'] != None:
                            mesh_props[obj['type']] = mesh_data_class(obj['prop_toggle_type'], obj['show'], obj['model_ref']['name'], obj['visible']).dictionary

                elif obj['trait_type']  == 'mesh_set':
                      mesh_sets[obj['type']] = mesh_set_data_class(obj['prop_selector_type'], obj['show'], obj['mesh_set'], 0).dictionary

                elif obj['trait_type']  == 'morph_set':
                      morph_sets[obj['type']] = morph_set_data_class(obj['prop_selector_type'], obj['show'], obj['morph_set'], 0, obj['model_ref']).dictionary
                      
                elif obj['trait_type']  == 'anim':
                      widget_type = obj['prop_toggle_type']
                      if obj['anim_loop'] == 'Clamp':
                            widget_type = obj['prop_anim_slider_type']
                      anim_props[obj['type']] = anim_prop_data_class(widget_type, obj['show'], obj['type'], obj['anim_loop'], obj['anim_start'], obj['anim_end'], obj['anim_blending'], obj['anim_weight'], obj['anim_play'], obj['model_ref']).dictionary
                      
                elif obj['trait_type']  == 'mat_prop' and 'mat_ref' in obj:
                      save_data = _mat_save_data(obj['mat_ref'], obj['mat_type'], obj['mat_reflective'], obj['mat_iridescent'], obj['mat_sheen'], obj['mat_emissive'])
                            
                      mat_props[obj['type']] = mat_prop_data_class(obj['prop_multi_widget_type'], obj['show'], obj['mat_ref']['name'], obj['mat_type'], obj['mat_emissive'], obj['mat_reflective'], obj['mat_iridescent'], obj['mat_sheen'], obj['mat_ref'], save_data).dictionary
                            
                elif obj['trait_type']  == 'mat_set':
                      mat_sets[obj['type']] = mat_set_data_class(obj['prop_selector_type'], obj['show'], obj['mat_set'], obj['mesh_set_name'], obj['material_id'], 0).dictionary

                      
                prop_label_data = property_label_data_class(obj['value_prop_label'], obj['call_prop_label'], obj['mesh_prop_label'], obj['mat_prop_label'], obj['anim_prop_label'], obj['mesh_set_label'], obj['morph_set_label'], obj['mat_set_label']).dictionary

      for i in menu_data:
          if i.isdigit():
                obj = menu_data[i]
                col_menu = menu_data_class(obj['menu_name'], obj['menu_primary_color'], obj['menu_secondary_color'],  obj['menu_text_color'], obj['menu_alignment']).dictionary
                if obj['collection_id'] == collection_id:
                      break
                  
      for i in action_data:
          if i.isdigit():
                obj = action_data[i]
                if obj['trait_type'] == 'mesh_action':
                      action_props[obj['type']] = action_mesh_data_class(obj['trait_type'], obj['action_set'], obj['mesh_interaction_type'], obj['sequence_type'],  obj['additive'],  obj['model_ref'])
                else:
                      action_props[obj['type']] = action_data_class(obj['trait_type'], obj['action_set'], obj['anim_interaction_type'], obj['sequence_type'],  obj['additive'])
                
                  
      data = collection_data_class(collection_name, collection_type, val_props, call_props, mesh_props, mesh_sets, morph_sets, anim_props, mat_props, mat_sets, col_menu, prop_label_data, node_data, action_props).json
      click.echo(data)


@click.command('collection-data')
@click.argument('collectionName', type=str)
@click.argument('collectionType', type=str)
@click.argument('valProps', type=dict)
@click.argument('meshProps', type=dict)
@click.argument('meshSets', type=dict)
@click.argument('animProps', type=dict)
@click.argument('matProps', type=dict)
@click.argument('materialSets', type=dict)
@click.argument('menuData', type=dict)
@click.argument('propLabelData', type=dict)
@click.argument('nodes', type=dict)
def collection_data(collectionName, collectionType, valProps, meshProps, meshSets, animProps, matProps, materialSets, menuData, propLabelData, nodes):
      """Return data for a single node property"""
      print(collection_data_class(collectionName, collectionType, valProps, meshProps, meshSets, animProps, matProps, materialSets, menuData, propLabelData, nodes).json)
      return collection_data_class(collectionName, collectionType, valProps, meshProps, meshSets, animProps, matProps, materialSets, menuData, propLabelData, nodes).json


@click.command('contract-data')
@click.argument('mintable', type=bool)
@click.argument('nft_type', type=str)
@click.argument('nft_chain', type=str)
@click.argument('nft_price', type=float)
@click.argument('prem_nft_price', type=float)
@click.argument('max_supply', type=int)
@click.argument('minter_type', type=str)
@click.argument('minter_name', type=str)
@click.argument('minter_desc', type=str)
@click.argument('minter_image', type=str)
@click.argument('minter_version', type=str)
def contract_data(mintable, nft_type, nft_chain, nft_price, prem_nft_price, max_supply, minter_type, minter_name, minter_desc, minter_image, minter_version):
      """Return data for contract data"""
      print(contract_data_class(mintable, nft_type, nft_chain, nft_price, prem_nft_price, max_supply, minter_type, minter_name, minter_desc, minter_image, minter_version).json)
      return contract_data_class(mintable, nft_type, nft_chain, nft_price, prem_nft_price, max_supply, minter_type, minter_name, minter_desc, minter_image, minter_version).json


@click.command('mat-prop-data')
@click.argument('name', type=str)
@click.argument('type', type=str)
@click.argument('emissive', type=int)
@click.argument('reflective', type=int)
@click.argument('irridescent', type=str)
@click.argument('sheen', type=bool)
@click.argument('mat_ref', type=dict)
@click.argument('widget_type', type=str)
@click.argument('show', type=bool)
def mat_prop_data(name, type, emissive, reflective, irridescent, sheen, mat_values, widget_type, show):
      """Return data for an material property"""
      save_data = _mat_save_data(mat_values, type, reflective, irridescent, sheen, emissive)
      print(mat_prop_data_class(widget_type, show, name, type, emissive, reflective, irridescent, sheen, mat_ref, save_data).json)
      return mat_prop_data_class(widget_type, show, name, type, emissive, reflective, irridescent, sheen, mat_ref, save_data).json


@click.command('anim-prop-data')
@click.argument('name', type=str)
@click.argument('loop', type=str)
@click.argument('start', type=int)
@click.argument('end', type=int)
@click.argument('blending', type=str)
@click.argument('weight', type=float)
@click.argument('play', type=bool)
@click.argument('model_ref', type=dict)
@click.argument('widget_type', type=str)
@click.argument('show', type=bool)
def anim_prop_data(name, loop, start, end, blending, weight, play, model_ref, widget_type, show):
      """Return data for a animation property"""
      print(anim_prop_data_class(widget_type, show, name, loop, start, end, blending, weight, play, model_ref).json)
      return anim_prop_data_class(widget_type, show, name, loop, start, end, blending, weight, play, model_ref).json


@click.command('mesh-set-data')
@click.argument('set', type=list)
@click.argument('selected_index', type=int)
@click.argument('widget_type', type=str)
@click.argument('show', type=bool)
def mesh_set_data(set, selected_index, widget_type, show):
      """Return data for a mesh set property"""
      print(mesh_set_data_class(widget_type, show, set, selected_index).json)
      return mesh_set_data_class(widget_type, show, set, selected_index).json


@click.command('single-node-data')
@click.argument('name', type=str)
@click.argument('type', type=str)
def single_node_data(name, type):
      """Return data for a single node property"""
      print(single_node_data_class(name, type).json)
      return single_node_data_class(name, type).json


@click.command('single-mesh-data')
@click.argument('name', type=str)
@click.argument('visible', type=bool)
def single_mesh_data(name, visible):
      """Return data for a single mesh property"""
      print(single_mesh_data_class(name, visible).json)
      return single_mesh_data_class(name, visible).json


@click.command('mesh-data')
@click.argument('name', type=str)
@click.argument('visible', type=bool)
@click.argument('widget_type', type=str)
@click.argument('show', type=bool)
def mesh_data(name, visible, widget_type, show):
      """Return data for mesh data"""
      print(mesh_data_class(widget_type, show, name, visible).json)
      return mesh_data_class(widget_type, show, name, visible).json


@click.command('single-float-data')
@click.argument('name', type=str)
@click.argument('default', type=int)
@click.argument('min', type=int)
@click.argument('max', type=int)
def single_float_data(name, default, min, max):
      """Return data for a float property"""
      print(single_float_data_class(name, default, min, max).json)
      return single_float_data_class(name, default, min, max).json


@click.command('slider-float-data')
@click.argument('default', type=float)
@click.argument('min', type=float)
@click.argument('max', type=float)
@click.argument('prop_slider_type', type=str)
@click.argument('prop_action_type', type=str)
@click.argument('widget_type', type=str)
@click.argument('show', type=bool)
def slider_float_data(default, min, max, prop_slider_type, prop_action_type, widget_type, show):
      """Return data for an int slider widget"""
      print(float_data_class(widget_type, show, prop_slider_type, prop_action_type, default, min, max).json)
      return float_data_class(widget_type, show, prop_slider_type, prop_action_type, default, min, max).json


@click.command('single-int-data')
@click.argument('name', type=str)
@click.argument('default', type=int)
@click.argument('min', type=int)
@click.argument('max', type=int)
def single_int_data(name, default, min, max):
      """Return data for a integer property"""
      print(single_int_data_class(name, default, min, max).json)
      return single_int_data_class(name, default, min, max).json


@click.command('slider-int-data')
@click.argument('default', type=int)
@click.argument('min', type=int)
@click.argument('max', type=int)
@click.argument('prop_slider_type', type=str)
@click.argument('prop_action_type', type=str)
@click.argument('widget_type', type=str)
@click.argument('show', type=bool)
def slider_int_data(default, min, max, prop_slider_type, prop_action_type, widget_type, show):
      """Return data for an int slider widget"""
      print(int_data_class(widget_type, show, prop_slider_type, prop_action_type, default, min, max).json)
      return int_data_class(widget_type, show, prop_slider_type, prop_action_type, default, min, max).json


@click.command('slider-data')
@click.argument('prop_slider_type', type=str)
@click.argument('prop_action_type', type=str)
@click.argument('widget_type', type=str)
@click.argument('show', type=bool)
def slider_data(prop_slider_type, prop_action_type, widget_type, show):
      """Return data for a slider widget"""
      print(slider_data_class(prop_slider_type, prop_action_type, widget_type, show).json)
      return slider_data_class(prop_slider_type, prop_action_type, widget_type, show).json


@click.command('menu-data')
@click.argument('name', type=str)
@click.argument('primary_color', type=str)
@click.argument('secondary_color', type=str)
@click.argument('text_color', type=str)
@click.argument('alignment', type=str)
def menu_data(name, primary_color, secondary_color, text_color, alignment):
      """Return data for hvym menu element"""
      print(menu_data_class(name, primary_color, secondary_color, text_color, alignment).json)
      return menu_data_class(name, primary_color, secondary_color, text_color, alignment).json


@click.command('basic-material-data')
@click.argument('color', type=str)
@click.option('--emissive', '-e', type=str,  help='Optional emissive color field')
@click.option('--emissive-intensity', '-ei', type=float,  help='Optional emissive intensity field')
def basic_material_data(color, emissive=None, emissive_intensity=None):
      """Return data for basic material"""
      print(basic_material_class(color, emissive, emissive_intensity).json)
      return basic_material_class(color, emissive, emissive_intensity).json


@click.command('lambert-material-data')
@click.argument('color', type=str)
@click.option('--emissive', '-e', type=str,  help='Optional emissive color field')
@click.option('--emissive-intensity', '-ei', type=float,  help='Optional emissive intensity field')
def lambert_material_data(color, emissive=None, emissive_intensity=None):
      """Return data for lambert material"""
      return phong_material_class(color, emissive, emissive_intensity).json


@click.command('phong-material-data')
@click.argument('color', type=str)
@click.argument('specular', type=str)
@click.argument('shininess', type=float)
@click.option('--emissive', '-e', type=str,  help='Optional emissive color field')
@click.option('--emissive-intensity', '-ei', type=float,  help='Optional emissive intensity field')
def phong_material_data(color, specular, shininess, emissive=None, emissive_intensity=None):
      """Return data for phong material"""
      return phong_material_class(color, specular, shininess, emissive, emissive_intensity).json


@click.command('standard-material-data')
@click.argument('color', type=str)
@click.argument('roughness', type=float)
@click.argument('metalness', type=float)
@click.option('--emissive', '-e', type=str,  help='Optional emissive color field')
@click.option('--emissive-intensity', '-ei', type=float,  help='Optional emissive intensity field')
def standard_material_data(color, roughness, metalness, emissive=None, emissive_intensity=None):
      """Return data for standard material"""
      return standard_material_class(color, roughness, metalness, emissive, emissive_intensity).json


@click.command('pbr-material-data')
@click.argument('color', type=str)
@click.argument('roughness', type=float)
@click.argument('metalness', type=float)
@click.option('--iridescent', '-i', type=bool,  help='Optional iridescence field')
@click.option('--sheen', '-s', type=float,  help='Optional sheen field')
@click.option('--sheen-roughness', '-sr', type=float,  help='Optional sheen roughness field')
@click.option('--sheen-color', '-sc', type=str,  help='Optional sheen color field')
@click.option('--emissive', '-e', type=str,  help='Optional emissive color field')
@click.option('--emissive-intensity', '-ei', type=float,  help='Optional emissive intensity field')
def pbr_material_data(color, roughness, metalness, iridescent=None, sheen=None, sheen_roughness=None, sheen_color=None, emissive=None, emissive_intensity=None):
      """Return data for pbr material"""
      return pbr_material_class(color, roughness, metalness, iridescent, sheen, sheen_roughness, sheen_color, emissive, emissive_intensity).json


@click.command('icp-install')
def icp_install():
      """Install ICP dfx cli."""
      cmd = "sh -c '$(curl -fsSL https://internetcomputer.org/install.sh)'"
      subprocess.run(cmd, shell=True, check=True)


@click.command('icp-new-cryptonym')
@click.argument('cryptonym', type=str)
def icp_new_cryptonym(cryptonym):
      """Create a new cryptonym, (alias/identity) for the Internet Computer Protocol."""
      command = f'dfx identity new {cryptonym} --storage-mode password-protected'
      output = subprocess.run(command, shell=True, capture_output=True, text=True)
      print('Command output:', output.stdout)


@click.command('icp-use-cryptonym')
@click.argument('cryptonym', type=str)
def icp_use_cryptonym(cryptonym):
      """Use a cryptonym, (alias/identity) for the Internet Computer Protocol."""
      command = f'dfx identity use {cryptonym}'
      output = subprocess.run(command, shell=True, capture_output=True, text=True)
      print('Command output:', output.stdout)


@click.command('icp-account')
def icp_account(cryptonym):
      """Get the account number for the current active account."""
      command = f'dfx ledger account-id'
      output = subprocess.run(command, shell=True, capture_output=True, text=True)
      print('Command output:', output.stdout)


@click.command('icp-principal')
def icp_principal():
      """Get the current principal id for account."""
      command = f'dfx identity get-principal'
      output = subprocess.run(command, shell=True, capture_output=True, text=True)
      click.echo(output.stdout)


@click.command('icp-principal-hash')
def icp_principal_hash():
      """Get the current principal id for account."""
      command = 'dfx identity get-principal'
      output = _call(command)
      hexdigest = _create_hex(output)
      click.echo(hexdigest.upper())


@click.command('icp-balance')
def icp_balance():
      """Get the current balance of ic for current account."""
      command = f'dfx ledger --network ic balance'
      output = subprocess.run(command, shell=True, capture_output=True, text=True)
      print('Command output:', output.stdout)


@click.command('icp-start-assets')
@click.argument('project_type')
def icp_start_assets(project_type): 
      """Start dfx in the current assets folder."""
      _set_hvym_network()
      if project_type == 'model':
            _futures('icp', [MODEL_TEMPLATE, 'Assets'], ['dfx start --clean --background'])
      elif project_type == 'minter':
            _futures('icp', [MINTER_TEMPLATE], ['dfx start --clean --background'])
                

@click.command('icp-stop-assets')
def icp_stop_assets():
      _futures('icp', [MODEL_TEMPLATE, 'Assets'], [ 'dfx stop'])


@click.command('icp-deploy-assets')
@click.argument('project_type')
@click.option('--test', is_flag=True, default=True, )
def icp_deploy_assets(project_type, test):
      """deploy the current asset canister."""
      command = 'dfx deploy'
      if not test:
        command += ' ic'

      folders = [MODEL_TEMPLATE, 'Assets']

      if project_type == 'minter':
            folders = [MINTER_TEMPLATE]
        
      return _subprocess('icp', folders, command, BUILDING_IMG)
    

@cli.command('icp-backup-keys')
@click.argument('identity_name')
@click.option('--out_path', type=click.Path(), required=True, help='The output path where to copy the identity.pem file.')
@click.option('--quiet', '-q', is_flag=True, default=False, help="Don't echo anything.")
def icp_backup_keys(identity_name, out_path, quiet):
      """Backup local Internet Computer Protocol keys."""
      # Get the home directory of the user
      home = os.path.expanduser("~") 

      # Construct the source path
      src_path = os.path.join(home, ".config", "dfx", "identity", identity_name, "identity.pem")

      # Check if the file exists
      if not os.path.exists(src_path):
        click.echo(f"The source .pem file does not exist: {src_path}")
        return
        
      # Construct the destination path
      dest_path = os.path.join(out_path, "identity.pem")

      # Copy the file to out_path
      shutil.copyfile(src_path, dest_path)

      click.echo(f"The keys have been successfully backed up at: {dest_path}")
    

@click.command('icp-project')
@click.argument('name')
@click.option('--quiet', '-q', is_flag=True,  required=False, default=False, help="Don't echo anything.")
def icp_project(name, quiet):
      """Create a new ICP project"""
      path = _new_session('icp', name)
      click.echo(f"Working Internet Computer Protocol directory set {path}")


@click.command('icp-project-path')
@click.option('--quiet', '-q', is_flag=True, default=False, help="Don't echo anything.")
def icp_project_path(quiet):
      """Print the current ICP project path"""
      click.echo(_get_session('icp'))
      

@click.command('icp-minter-path')
@click.option('--quiet', '-q', is_flag=True, default=False, help="Don't echo anything.")
def icp_minter_path(quiet):
      """Print the current ICP active project minter path"""
      click.echo(_ic_minter_path())

@click.command('icp-minter-model-path')
@click.option('--quiet', '-q', is_flag=True, default=False, help="Don't echo anything.")
def icp_minter_model_path(quiet):
      """Print the current ICP active project minter path"""
      click.echo(_ic_minter_model_path())

@click.command('icp-model-path')
@click.option('--quiet', '-q', is_flag=True, default=False, help="Don't echo anything.")
def icp_model_path(quiet):
      """Print the current ICP active project minter path"""
      click.echo(_ic_model_path())


@click.command('icp-init')
@click.option('--force', '-f', is_flag=True, default=False, help='Overwrite existing directory without asking for confirmation')
@click.option('--quiet', '-q', is_flag=True, default=False, help="Don't echo anything.")
def icp_init(force, quiet):
      """Intialize project directories"""
      model_path = _ic_model_path()
      minter_path = _ic_minter_path()

      if not (os.path.exists(model_path) and os.path.exists(minter_path)) or force:
        if not (force or click.confirm(f"Do you want to create a new deploy dir at {model_path}?")):
            return
      if not os.path.exists(model_path):
            _ic_create_model_repo(model_path)
      if not os.path.exists(minter_path):
            _ic_create_model_minter_repo(_get_session('icp'))
            try:
                  _subprocess_output('npm install', minter_path) 
                
            except Exception as e:  
                  print("Command failed with error:", str(e))
            
      click.echo(f"Project files created at: {model_path} and {minter_path}.")


@click.command('icp-debug-model')
@click.argument('model', type=str)
def icp_debug_model(model):
      """Set up nft collection deploy directories & render model debug templates."""
      path = _ic_model_path()
      assets_dir = os.path.join(path, 'Assets')
      src_dir = os.path.join(assets_dir, 'src')
      model_path = os.path.join(src_dir, model)
      model_name = model.replace('.glb', '')
      js_file_name = 'main.js'

      if not os.path.exists(model_path):
        click.echo(f"No model exists at path {model_path}.")

      js_dir = os.path.join(src_dir, 'assets')

      if not os.path.exists(js_dir):
        os.makedirs(js_dir)
        
      file_loader = FileSystemLoader(FILE_PATH / 'templates')
      env = Environment(loader=file_loader)
      template = env.get_template(TEMPLATE_MODEL_VIEWER_JS)

      data = model_debug_data(model, model_name, js_file_name)
      output = template.render(data=data)
      js_file_path = os.path.join(src_dir, 'assets',  js_file_name)
      index_file_path = os.path.join(src_dir, 'index.html')

      with open(js_file_path, 'w') as f:
        output = template.render(data=data)
        f.write(output)
        
      template = env.get_template(TEMPLATE_MODEL_VIEWER_INDEX)

      with open(index_file_path, 'w') as f:
        output = template.render(data=data)
        f.write(output)


@click.command('icp-debug-model-minter')
@click.argument('model', type=str)
def icp_debug_model_minter(model):
      """Set up nft collection deploy directories"""
      loading = GifAnimation(LOADING_IMG, 1000, True, '', True)
      loading.Play()
      hvym_data = None

      if '.glb' not in model:
        click.echo(f"Only GLTF Binary files (.glb) accepted.")
        return

      model_path = os.path.join(_ic_minter_model_path(), model)

      gltf = GLTF2().load(model_path)
      if 'HVYM_nft_data' in gltf.extensions.keys():
        hvym_data = gltf.extensions['HVYM_nft_data']
      else:
        click.echo("No Heavymeta Data in model.")
        return

      all_val_props = {}
      all_call_props = {}
      contract_props = None
      data = {}
      command = 'dfx identity get-principal'
      output = _call(command)
      creator_hash = _create_hex(output).upper()

      for key, value in hvym_data.items():
          if key != 'contract':
                for propType, props in value.items():
                      if propType == 'valProps':
                            for name, prop in props.items():
                                  if prop['prop_action_type'] != 'Static' and not prop['immutable']:
                                        all_val_props[name] = prop
                      if propType == 'callProps':
                            for name, prop in props.items():
                                  all_call_props[name] = prop
          else:
                contract_props = value

      data['valProps'] = all_val_props
      data['callProps'] = all_call_props
      data['contract'] = contract_props
      data['creatorHash'] = creator_hash
      data['model'] = model
      
      path = os.path.join(_ic_minter_path(), 'src', 'proprium_minter_backend')

      file_loader = FileSystemLoader(FILE_PATH / 'templates')
      env = Environment(loader=file_loader)
      template = env.get_template(TEMPLATE_MODEL_MINTER_MAIN)
      out_file_path = os.path.join(path,  'main.mo')

      with open(out_file_path, 'w') as f:
        output = template.render(data=data)
        f.write(output)

      template = env.get_template(TEMPLATE_MODEL_MINTER_TYPES)
      out_file_path = os.path.join(path,  'Types.mo')

      with open(out_file_path, 'w') as f:
        output = template.render(data=data)
        f.write(output)

      path = os.path.join(_ic_minter_path(),  'src', 'proprium_minter_frontend', 'src')
      template = env.get_template(TEMPLATE_MODEL_MINTER_INDEX)
      out_file_path = os.path.join(path,  'index.html')

      with open(out_file_path, 'w') as f:
        output = template.render(data=data)
        f.write(output)

      template = env.get_template(TEMPLATE_MODEL_MINTER_JS)
      out_file_path = os.path.join(path,  'index.js')

      with open(out_file_path, 'w') as f:
        output = template.render(data=data)
        f.write(output)

      loading.Stop()



@click.command('test')
def test():
      """Set up nft collection deploy directories"""
      loading = GifAnimation(LOADING_IMG, 1000, True, '', True)

      time.sleep(3)

      loading.Play()

      time.sleep(10)

      loading.Stop()



@click.command('print-hvym-data')
@click.argument('path', type=str)
def print_hvym_data(path):
      """Print Heavymeta data embedded in glb file."""
      if '.glb' not in path:
        click.echo(f"Only GLTF Binary files (.glb) accepted.")
        return
      gltf = GLTF2().load(path)
      if 'HVYM_nft_data' in gltf.extensions.keys():
        hvym_data = gltf.extensions['HVYM_nft_data']
        pretty_json = json.dumps(hvym_data, indent=4)
        print(pretty_json)
      else:
        click.echo(f"No Heavymeta data in file: {path}")
        

@click.command('version')
def version():
      """Print the version number."""
      click.echo(VERSION)

@click.command('about')
def about():
      """About this cli"""
      click.echo(ABOUT)


cli.add_command(parse_blender_hvym_interactables)
cli.add_command(parse_blender_hvym_collection)
cli.add_command(contract_data)
cli.add_command(collection_data)
cli.add_command(contract_data)
cli.add_command(mat_prop_data)
cli.add_command(anim_prop_data)
cli.add_command(mesh_set_data)
cli.add_command(single_node_data)
cli.add_command(single_mesh_data)
cli.add_command(mesh_data)
cli.add_command(single_float_data)
cli.add_command(slider_float_data)
cli.add_command(single_int_data)
cli.add_command(slider_int_data)
cli.add_command(slider_data)
cli.add_command(menu_data)
cli.add_command(basic_material_data)
cli.add_command(lambert_material_data)
cli.add_command(phong_material_data)
cli.add_command(standard_material_data)
cli.add_command(pbr_material_data)
cli.add_command(icp_install)
cli.add_command(icp_new_cryptonym)
cli.add_command(icp_use_cryptonym)
cli.add_command(icp_account)
cli.add_command(icp_principal)
cli.add_command(icp_principal_hash)
cli.add_command(icp_balance)
cli.add_command(icp_start_assets)
cli.add_command(icp_stop_assets)
cli.add_command(icp_deploy_assets)
cli.add_command(icp_backup_keys)
cli.add_command(icp_project)
cli.add_command(icp_project_path)
cli.add_command(icp_minter_path)
cli.add_command(icp_minter_model_path)
cli.add_command(icp_model_path)
cli.add_command(icp_init)
cli.add_command(icp_debug_model)
cli.add_command(icp_debug_model_minter)
cli.add_command(test)
cli.add_command(print_hvym_data)
cli.add_command(version)
cli.add_command(about)

if __name__ == '__main__':
    cli()
