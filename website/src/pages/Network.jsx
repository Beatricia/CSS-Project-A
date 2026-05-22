import { useState } from 'react';
import './Network.css';

const BASE_URL = import.meta.env.BASE_URL;

const NETWORK_SOURCES = {
  main: `${BASE_URL}network/selected_song_artist_network.html`,
  ukraineRussiaPre: `${BASE_URL}network/prepost/ukraine_russia_pre_network.html`,
  ukraineRussiaPost: `${BASE_URL}network/prepost/ukraine_russia_post_network.html`,
  israelPalestinePre: `${BASE_URL}network/prepost/israel_palestine_pre_network.html`,
  israelPalestinePost: `${BASE_URL}network/prepost/israel_palestine_post_network.html`,
};

const TAB_CONFIG = [
  {
    id: 'main',
    label: 'Main Graph',
    title: 'Selected-Song Collaboration Network',
    intro:
      'This is the full selected-song network used as the project’s main collaboration view.',
    metrics: [
      { label: 'Nodes', value: '16' },
      { label: 'Edges', value: '15' },
      { label: 'Successful Recording Matches', value: '81' },
      { label: '2+ Credit Recordings', value: '10' },
    ],
    interpretation: [
      'The collaboration network shows artists as nodes and shared MusicBrainz recording credits as edges. Larger nodes represent artists with more collaboration activity within the selected-song dataset, and thicker edges represent repeated collaborations. The full network is not a complete map of every collaboration by every artist; it is the final selected-song collaboration network built from the project’s curated song dataset and MusicBrainz recording-credit matches.',
      'In the main graph, the strongest cluster is centered around Ukrainian artists alyona alyona and Jerry Heil. Their repeated connection reflects multiple shared recordings, including “Dai Boh” and “KUPALA.” This creates the densest part of the network, with additional Ukrainian and Eastern European collaborators such as Alina Pash, Olexesh, Ela, Monika Liu, Evgeny Khmara, and MONATIK appearing around them. Saint Levant forms another smaller collaboration cluster, connecting to artists such as Kehlani, MC Abdul, and Playyard. These clusters suggest that collaboration in the selected dataset is concentrated around a few highly connected artists rather than evenly distributed across all artists.',
      'Across the main selected-song network, the visual structure is sparse but interpretable: the most prominent relationships are repeated, explicit recording-level collaborations rather than inferred associations.',
    ],
    content: (
      <div className="network-iframe-shell">
        <iframe
          title="Selected Song Artist Collaboration Network"
          src={NETWORK_SOURCES.main}
          className="network-iframe"
        />
      </div>
    ),
  },
  {
    id: 'ukraine-russia',
    label: 'Ukraine/Russia War',
    title: 'Ukraine/Russia Pre/Post Comparison',
    intro:
      'These two graphs split the selected-song collaboration network at the 2022 conflict start year.',
    metrics: [
      { label: 'Pre Nodes', value: '3' },
      { label: 'Pre Edges', value: '2' },
      { label: 'Post Nodes', value: '6' },
      { label: 'Post Edges', value: '8' },
    ],
    interpretation: [
      'The Ukraine/Russia pre-conflict graph is small, with alyona alyona connected to Alina Pash and Olexesh before 2022. In the post-conflict graph, the network becomes visibly more connected around alyona alyona and Jerry Heil. Jerry Heil appears as a central post-conflict collaborator, linking to MONATIK, Evgeny Khmara, Monika Liu, and Ela.',
      'Within this selected-song dataset, the post-2022 Ukraine/Russia graph shows a denser collaboration structure than the pre-2022 graph. This should not be interpreted as a universal claim about all Ukrainian or Russian music, but it does suggest that the selected songs captured more post-conflict collaboration activity among the matched artists.',
    ],
    content: (
      <div className="network-comparison-grid">
        <div className="network-graph-card">
          <div className="comparison-card-header">
            <h3>Pre-conflict</h3>
            <span>Ukraine/Russia collaboration network before 2022</span>
          </div>
          <div className="network-iframe-shell">
            <iframe
              title="Ukraine Russia Pre-conflict Collaboration Network"
              src={NETWORK_SOURCES.ukraineRussiaPre}
              className="network-iframe"
            />
          </div>
        </div>
        <div className="network-graph-card">
          <div className="comparison-card-header">
            <h3>Post-conflict</h3>
            <span>Ukraine/Russia collaboration network from 2022 onward</span>
          </div>
          <div className="network-iframe-shell">
            <iframe
              title="Ukraine Russia Post-conflict Collaboration Network"
              src={NETWORK_SOURCES.ukraineRussiaPost}
              className="network-iframe"
            />
          </div>
        </div>
      </div>
    ),
  },
  {
    id: 'israel-palestine',
    label: 'Israel/Palestine War',
    title: 'Israel/Palestine Pre/Post Comparison',
    intro:
      'These two graphs split the selected-song collaboration network at the 2023 conflict start year.',
    metrics: [
      { label: 'Pre Nodes', value: '4' },
      { label: 'Pre Edges', value: '2' },
      { label: 'Post Nodes', value: '5' },
      { label: 'Post Edges', value: '3' },
    ],
    interpretation: [
      'The Israel/Palestine pre-conflict graph shows two separate pairs: Saint Levant connected to Playyard, and Yasmin Levy connected to Concha Buika. These are disconnected components, meaning the selected pre-2023 collaborations do not form one shared cluster.',
      'The post-conflict graph shows Saint Levant as the clearest central figure, connected to Kehlani and MC Abdul, while Bashar Murad and Sabreen form a separate collaboration pair. Within the selected-song dataset, the post-2023 graph suggests a small but meaningful collaboration structure around Palestinian-associated artists, especially Saint Levant and Bashar Murad.',
    ],
    content: (
      <div className="network-comparison-grid">
        <div className="network-graph-card">
          <div className="comparison-card-header">
            <h3>Pre-conflict</h3>
            <span>Israel/Palestine collaboration network before 2023</span>
          </div>
          <div className="network-iframe-shell">
            <iframe
              title="Israel Palestine Pre-conflict Collaboration Network"
              src={NETWORK_SOURCES.israelPalestinePre}
              className="network-iframe"
            />
          </div>
        </div>
        <div className="network-graph-card">
          <div className="comparison-card-header">
            <h3>Post-conflict</h3>
            <span>Israel/Palestine collaboration network from 2023 onward</span>
          </div>
          <div className="network-iframe-shell">
            <iframe
              title="Israel Palestine Post-conflict Collaboration Network"
              src={NETWORK_SOURCES.israelPalestinePost}
              className="network-iframe"
            />
          </div>
        </div>
      </div>
    ),
  },
];

function Network() {
  const [activeTab, setActiveTab] = useState('main');
  const currentTab = TAB_CONFIG.find((tab) => tab.id === activeTab) ?? TAB_CONFIG[0];

  return (
    <div className="network-page">
      <section className="page-header">
        <h1>Artist Collaboration Network</h1>
        <p>Selected-song MusicBrainz collaboration graphs with conflict-specific comparisons</p>
      </section>

      <section className="section">
        <div className="container">
          <h2>Methodology</h2>
          <p className="section-intro">
            These visualizations use selected songs from the project dataset, not full discographies.
            Node = artist, edge = MusicBrainz recording collaboration, and edge weight = number of
            shared selected-song recordings.
          </p>

          <div className="patterns-grid network-notes-grid" style={{ marginBottom: '2rem' }}>
            <div className="pattern-card">
              <h3>How To Read The Graphs</h3>
              <p>Node = artist.</p>
              <p>Edge = artists credited on the same MusicBrainz recording.</p>
              <p>Edge weight = number of shared selected-song recordings.</p>
            </div>
            <div className="pattern-card">
              <h3>Scope And Split</h3>
              <p>The network is limited to selected songs and high-confidence MusicBrainz matches.</p>
              <p>The pre/post split uses each recording’s year relative to the conflict start year.</p>
              <p>Syria’s pre/post graphs were empty, so they are not included in the tab UI.</p>
            </div>
          </div>

          <div className="network-tabs" role="tablist" aria-label="Network views">
            {TAB_CONFIG.map((tab) => (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={activeTab === tab.id}
                className={`network-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="tab-panel" role="tabpanel" aria-label={currentTab.title}>
            <div className="tab-panel-header">
              <div>
                <h2>{currentTab.title}</h2>
                <p className="section-intro tab-panel-intro">{currentTab.intro}</p>
              </div>
            </div>

            <div className="preview-grid network-metrics-grid" style={{ marginBottom: '2rem' }}>
              {currentTab.metrics.map((metric) => (
                <div className="preview-card" key={metric.label}>
                  <h4>{metric.value}</h4>
                  <p>{metric.label}</p>
                </div>
              ))}
            </div>

            <div className="tab-graph-stack">{currentTab.content}</div>
          </div>

            <h2>Interpretation</h2>
            <div className="network-interpretation-card">
              {currentTab.interpretation.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
          </div>

            <h2>Data Limitations and Interpretation Notes</h2>
            <div className="network-limitation-card">
              <p>
                This is the final selected-song collaboration network, not a full-discography network.
              </p>
              <p>
                The project intentionally used songs already included in the dataset instead of scraping
                every song by every artist. That kept the method focused and computationally realistic.
              </p>
              <p>
                MusicBrainz metadata is uneven across artists, countries, languages, transliterations,
                and release types. Some artists from the project dataset could not be matched to
                MusicBrainz with high confidence, and some song titles did not match recording entries,
                especially when titles had alternate spellings, translations, punctuation,
                featured-artist formatting, or non-Latin scripts.
              </p>
              <p>
                The final network only includes recordings where MusicBrainz returned a usable match and
                where the recording had two or more credited artists. Because of these filters,
                isolated artists and unmatched songs are not shown, which makes the visible graph
                smaller than the full artist dataset.
              </p>
              <p>
                The pre/post graphs should be interpreted as selected-song evidence, not as complete
                representations of all collaborations before and after each conflict.
              </p>
              <p className="network-limitation-conclusion">
                These limitations make the network conservative: it likely undercounts collaborations,
                but the edges that remain are more reliable. As a result, the graph is best read as a
                high-confidence collaboration snapshot within the selected project dataset, rather than
                a complete map of the global music industry.
              </p>
            </div>
        </div>
      </section>
    </div>
  );
}

export default Network;
