############################################################################
#                                                                          #
# Copyright (c) 2017 eBay Inc.                                             #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#  http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
#                                                                          #
############################################################################

from __future__ import division
from __future__ import absolute_import

description = r'''
Rewrite a dataset (or chain to previous) with new hashlabel.
'''

from shutil import copyfileobj

from extras import OptionString, job_params
from dataset import DatasetWriter

options = {
	'hashlabel'                 : OptionString,
	'caption'                   : '"%(caption)s" hashed on %(hashlabel)s',
	'length'                    : -1, # Go back at most this many datasets. You almost always want -1 (which goes until previous.source)
	'as_chain'                  : False, # one dataset per slice (avoids rewriting at the end)
}

datasets = ('source', 'previous',)

def prepare(params):
	d = datasets.source
	caption = options.caption % dict(caption=d.caption, hashlabel=options.hashlabel)
	prev_p = job_params(datasets.previous, default_empty=True)
	prev_source = prev_p.datasets.source
	if len(d.chain(stop_jobid=prev_source, length=options.length)) == 1:
		filename = d.filename
	else:
		filename = None
	dws = []
	previous = datasets.previous
	for sliceno in range(params.slices):
		if options.as_chain and sliceno == params.slices - 1:
			name = "default"
		else:
			name = str(sliceno)
		dw = DatasetWriter(
			caption="%s (slice %d)" % (caption, sliceno),
			hashlabel=options.hashlabel,
			filename=filename,
			previous=previous,
			name=name,
			for_single_slice=sliceno,
		)
		previous = (params.jobid, name)
		dws.append(dw)
	names = []
	for n, c in d.columns.items():
		# names has to be in the same order as the add calls
		# so the iterator returns the same order the writer expects.
		names.append(n)
		for dw in dws:
			dw.add(n, c.type)
	return dws, names, prev_source, caption, filename

def analysis(sliceno, prepare_res):
	dws, names, prev_source = prepare_res[:3]
	it = datasets.source.iterate_chain(
		sliceno,
		names,
		stop_jobid=prev_source,
		length=options.length,
	)
	write = dws[sliceno].get_split_write_list()
	for values in it:
		write(values)

def synthesis(prepare_res, params):
	if not options.as_chain:
		# If we don't want a chain we abuse our knowledge of dataset internals
		# to avoid recompressing. Don't do this stuff yourself.
		dws, names, prev_source, caption, filename = prepare_res
		merged_dw = DatasetWriter(
			caption=caption,
			hashlabel=options.hashlabel,
			filename=filename,
			previous=datasets.previous,
			meta_only=True,
			columns=datasets.source.columns,
		)
		for sliceno in range(params.slices):
			merged_dw.set_lines(sliceno, sum(dw._lens[sliceno] for dw in dws))
			for dwno, dw in enumerate(dws):
				merged_dw.set_minmax((sliceno, dwno), dw._minmax[sliceno])
			for n in names:
				fn = merged_dw.column_filename(n, sliceno=sliceno)
				with open(fn, "wb") as out_fh:
					for dw in dws:
						fn = dw.column_filename(n, sliceno=sliceno)
						with open(fn, "rb") as in_fh:
							copyfileobj(in_fh, out_fh)
		for dw in dws:
			dw.discard()
