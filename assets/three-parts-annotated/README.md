# Three-part diagram annotations

`annotations.yaml` is the editable source for the five-marker diagram used on the data model page. Edit annotation text here, keeping a blank line between paragraphs. The JPG is the source diagram. The generated embed lives in `templates/components/three-parts-no-a6.embed.html` and is included by `templates/data_model.html`.

To regenerate the embed, use the `image-annotation` environment in the image-annotations repository and render this YAML with `--format embed`. Validate the generated file before updating the viewer component. The source meeting transcript is kept with the planning application project notes and is not copied into this viewer repository.
