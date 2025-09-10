from flask import Blueprint, request, jsonify
import logging
from services.stream_service import get_stream_processor

# Create blueprint for display filter routes
display_filter_bp = Blueprint('display_filter', __name__)

@display_filter_bp.route('/render-all-ids', methods=['POST'])
def render_all_ids():
    """
    Endpoint to set display mode to show all IDs
    Sets display_all_ids to True without changing the ids_to_display array
    """
    try:
        # Get the stream processor instance
        stream_processor = get_stream_processor()
        
        if not stream_processor:
            return jsonify({
                'success': False,
                'message': 'Stream processor not initialized'
            }), 400
        
        # Set display mode to all IDs (boolean to True, no change to array)
        success = stream_processor.set_display_all_ids(display_all=True)
        
        if success:
            # Get current filter info for response
            filter_info = stream_processor.get_display_filter_info()
            
            logging.info("Display mode set to render all IDs")
            return jsonify({
                'success': True,
                'message': 'Display mode set to show all IDs',
                'filter_info': filter_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to set display mode'
            }), 500
            
    except Exception as e:
        logging.error(f"Error in render_all_ids endpoint: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

@display_filter_bp.route('/render-specific-ids', methods=['POST'])
def render_specific_ids():
    """
    Endpoint to set display mode to show specific IDs or exclude specific IDs
    Updates the ids_to_display array and sets display_all_ids to False
    
    Expected JSON payload:
    {
        "ids": ["id1", "id2", "id3"],
        "mode": "include" | "exclude"  // Optional, defaults to "include"
    }
    """
    logging.info("Received request to render specific IDs")
    try:
        # Get the stream processor instance
        stream_processor = get_stream_processor()
        
        if not stream_processor:
            return jsonify({
                'success': False,
                'message': 'Stream processor not initialized'
            }), 400
        
        # Get the JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        # Extract the IDs array and mode from the request
        ids_list = data.get('ids', [])
        mode = data.get('mode', 'include')  # Default to include for backwards compatibility
        
        logging.info(f"IDs to process: {ids_list}, Mode: {mode}")
        
        # Validate that ids is a list
        if not isinstance(ids_list, list):
            return jsonify({
                'success': False,
                'message': 'IDs must be provided as an array'
            }), 400
        
        # Validate mode
        if mode not in ['include', 'exclude']:
            return jsonify({
                'success': False,
                'message': 'Mode must be either "include" or "exclude"'
            }), 400
        
        # Convert all IDs to strings and filter out empty ones
        clean_ids = [str(id_val).strip() for id_val in ids_list if str(id_val).strip()]
        
        # Set specific IDs based on mode
        if mode == 'include':
            success = stream_processor.set_specific_ids_to_display(clean_ids, mode='include')
            action_message = f'Display mode set to show only specific IDs: {clean_ids}'
        else:  # mode == 'exclude'
            success = stream_processor.set_specific_ids_to_display(clean_ids, mode='exclude')
            action_message = f'Display mode set to exclude specific IDs: {clean_ids}'
        
        if success:
            # Get current filter info for response
            filter_info = stream_processor.get_display_filter_info()
            
            logging.info(action_message)
            return jsonify({
                'success': True,
                'message': action_message,
                'filter_info': filter_info,
                'ids_count': len(clean_ids),
                'mode': mode
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to set {mode} mode for specific IDs'
            }), 500
            
    except Exception as e:
        logging.error(f"Error in render_specific_ids endpoint: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

# @display_filter_bp.route('/render-specific-ids', methods=['POST'])
# def render_specific_ids():
#     """
#     Endpoint to set display mode to show specific IDs
#     Updates the ids_to_display array and sets display_all_ids to False
    
#     Expected JSON payload:
#     {
#         "ids": ["id1", "id2", "id3"]
#     }
#     """
#     logging.info("Received request to render specific IDs")
#     try:
#         # Get the stream processor instance
#         stream_processor = get_stream_processor()
        
#         if not stream_processor:
#             return jsonify({
#                 'success': False,
#                 'message': 'Stream processor not initialized'
#             }), 400
        
#         # Get the JSON data from request
#         data = request.get_json()
        
#         if not data:
#             return jsonify({
#                 'success': False,
#                 'message': 'No JSON data provided'
#             }), 400
        
#         # Extract the IDs array from the request
#         ids_list = data.get('ids', [])
#         logging.info(f"IDs to render: {ids_list}")
#         # Validate that ids is a list
#         if not isinstance(ids_list, list):
#             return jsonify({
#                 'success': False,
#                 'message': 'IDs must be provided as an array'
#             }), 400
        
#         # Convert all IDs to strings and filter out empty ones
#         clean_ids = [str(id_val).strip() for id_val in ids_list if str(id_val).strip()]
        
#         # Set specific IDs to display (this also sets display_all_ids to False)
#         success = stream_processor.set_specific_ids_to_display(clean_ids)
        
#         if success:
#             # Get current filter info for response
#             filter_info = stream_processor.get_display_filter_info()
            
#             logging.info(f"Display mode set to render specific IDs: {clean_ids}")
#             return jsonify({
#                 'success': True,
#                 'message': f'Display mode set to show specific IDs: {clean_ids}',
#                 'filter_info': filter_info,
#                 'ids_count': len(clean_ids)
#             }), 200
#         else:
#             return jsonify({
#                 'success': False,
#                 'message': 'Failed to set specific IDs display mode'
#             }), 500
            
#     except Exception as e:
#         logging.error(f"Error in render_specific_ids endpoint: {e}")
#         return jsonify({
#             'success': False,
#             'message': f'Internal server error: {str(e)}'
#         }), 500

@display_filter_bp.route('/get-display-filter-info', methods=['GET'])
def get_display_filter_info():
    """
    Endpoint to get current display filter information
    Returns the current display mode and IDs being filtered
    """
    try:
        # Get the stream processor instance
        stream_processor = get_stream_processor()
        
        if not stream_processor:
            return jsonify({
                'success': False,
                'message': 'Stream processor not initialized'
            }), 400
        
        # Get current filter info
        filter_info = stream_processor.get_display_filter_info()
        
        return jsonify({
            'success': True,
            'filter_info': filter_info
        }), 200
        
    except Exception as e:
        logging.error(f"Error in get_display_filter_info endpoint: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

# Additional utility endpoint to clear specific IDs
@display_filter_bp.route('/clear-specific-ids', methods=['POST'])
def clear_specific_ids():
    """
    Endpoint to clear all specific IDs and set display mode to all IDs
    This is equivalent to calling render_all_ids but also clears the ids array
    """
    try:
        # Get the stream processor instance
        stream_processor = get_stream_processor()
        
        if not stream_processor:
            return jsonify({
                'success': False,
                'message': 'Stream processor not initialized'
            }), 400
        
        # Clear specific IDs and set to display all
        stream_processor.set_specific_ids_to_display([])  # Clear the array
        success = stream_processor.set_display_all_ids(display_all=True)  # Set to all
        
        if success:
            # Get current filter info for response
            filter_info = stream_processor.get_display_filter_info()
            
            logging.info("Cleared specific IDs and set display mode to all IDs")
            return jsonify({
                'success': True,
                'message': 'Cleared specific IDs and set display mode to show all IDs',
                'filter_info': filter_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to clear specific IDs'
            }), 500
            
    except Exception as e:
        logging.error(f"Error in clear_specific_ids endpoint: {e}")
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500